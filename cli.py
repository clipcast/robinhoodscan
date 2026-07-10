"""
RobinhoodScan — CLI Interface
==============================
Track transactions, blocks, addresses, and tokens on Robinhood Chain.
"""
import argparse
import json
import csv
import os
import sys
import time
import yaml
from api_client import BlockscoutClient


def load_config(path="config.yaml"):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}


def save_csv(rows, path, fieldnames=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        print("[INFO] No data to save.")
        return
    if not fieldnames:
        fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[INFO] Saved {len(rows)} rows to {path}")


def cmd_stats(client, args):
    """Show network statistics."""
    stats = client.get_stats()
    if not stats:
        print("[ERROR] Could not fetch stats")
        return
    print("\n" + "=" * 50)
    print("  Robinhood Chain — Network Stats")
    print("=" * 50)
    print(f"  Total Blocks:       {stats.get('total_blocks','—')}")
    print(f"  Total Transactions: {stats.get('total_transactions','—')}")
    print(f"  Total Addresses:    {stats.get('total_addresses','—')}")
    print(f"  Transactions Today: {stats.get('transactions_today','—')}")
    print(f"  ETH Price:          ${stats.get('coin_price','—')}")
    print(f"  Avg Block Time:     {stats.get('average_block_time','—')}s")
    print(f"  Gas (fast):         {stats.get('gas_prices',{}).get('fast','—')} Gwei")
    print(f"  Gas (avg):          {stats.get('gas_prices',{}).get('average','—')} Gwei")
    print(f"  Market Cap:         ${stats.get('market_cap','—')}")
    print("=" * 50)
    if args.output:
        save_csv([stats], args.output)


def cmd_txs(client, args):
    """Show latest transactions."""
    data = client.get_latest_transactions()
    items = (data or {}).get("items", [])
    if not items:
        print("[INFO] No transactions found")
        return
    print(f"\n{'='*90}")
    print(f"  Latest Transactions — {len(items)} shown")
    print(f"{'='*90}")
    print(f"{'HASH':<24} {'FROM':<16} {'TO':<16} {'VALUE (ETH)':>14} {'STATUS':<8} {'AGE':<10}")
    print("-" * 90)
    for t in items[:args.limit]:
        h = BlockscoutClient.format_hash
        ta = BlockscoutClient.time_ago
        val = BlockscoutClient.wei_to_eth(t.get("value", "0"))
        frm = h((t.get("from") or {}).get("hash", ""), 8, 4)
        to_obj = t.get("to")
        to = h(to_obj.get("hash", ""), 8, 4) if isinstance(to_obj, dict) else "—"
        status = "✓ OK" if t.get("status") == "ok" else "✗ FAIL"
        print(f"{h(t.get('hash',''),14,6):<24} {frm:<16} {to:<16} {val:>14.4f} {status:<8} {ta(t.get('timestamp')):<10}")
    print("=" * 90)
    if args.output:
        flat = []
        for t in items[:args.limit]:
            flat.append({
                "hash": t.get("hash"),
                "from": (t.get("from") or {}).get("hash"),
                "to": (t.get("to") or {}).get("hash") if isinstance(t.get("to"), dict) else "",
                "value_eth": BlockscoutClient.wei_to_eth(t.get("value", "0")),
                "status": t.get("status"),
                "block": t.get("block_number"),
                "timestamp": t.get("timestamp"),
                "gas_used": t.get("gas_used"),
                "fee": (t.get("fee") or {}).get("value"),
            })
        save_csv(flat, args.output)


def cmd_blocks(client, args):
    """Show latest blocks."""
    data = client.get_latest_blocks()
    items = (data or {}).get("items", [])
    if not items:
        print("[INFO] No blocks found")
        return
    print(f"\n{'='*70}")
    print(f"  Latest Blocks — {len(items)} shown")
    print(f"{'='*70}")
    print(f"{'BLOCK':>10} {'GAS USED':>14} {'SIZE':>10} {'AGE':<12}")
    print("-" * 70)
    for b in items[:args.limit]:
        ta = BlockscoutClient.time_ago
        gas = int(b.get("gas_used", 0))
        print(f"#{b.get('height',''):>9} {gas:>14,} {b.get('size','—'):>10} {ta(b.get('timestamp')):<12}")
    print("=" * 70)
    if args.output:
        save_csv(items[:args.limit], args.output)


def cmd_address(client, args):
    """Show address info and transactions."""
    addr = args.address
    info = client.get_address(addr)
    txs_data = client.get_address_transactions(addr)
    txs = (txs_data or {}).get("items", [])

    w2e = BlockscoutClient.wei_to_eth
    h = BlockscoutClient.format_hash
    ta = BlockscoutClient.time_ago

    print(f"\n{'='*60}")
    print(f"  Address: {addr}")
    print(f"{'='*60}")
    if info:
        print(f"  Balance:     {w2e(info.get('coin_balance','0')):.6f} ETH")
        print(f"  Tx Count:    {info.get('tx_count','—')}")
        print(f"  Is Contract: {info.get('is_contract',False)}")
        print(f"  Name:        {info.get('name','—')}")
    else:
        print("  [WARN] Could not fetch address info")
    print(f"  Transactions ({len(txs)} shown):")
    print("-" * 60)
    for t in txs[:args.limit]:
        val = w2e(t.get("value", "0"))
        status = "✓" if t.get("status") == "ok" else "✗"
        frm = h((t.get("from") or {}).get("hash", ""), 8, 4)
        print(f"  {status} {h(t.get('hash',''),12,6)} {frm} → {val:.4f} ETH {ta(t.get('timestamp'))}")
    print("=" * 60)
    if args.output and txs:
        save_csv(txs[:args.limit], args.output)


def cmd_token(client, args):
    """Show token info."""
    token = client.get_token(args.address)
    if not token:
        print("[ERROR] Token not found")
        return
    print(f"\n{'='*50}")
    print(f"  Token: {token.get('symbol','')} — {token.get('name','')}")
    print(f"{'='*50}")
    print(f"  Type:       {token.get('type','—')}")
    print(f"  Address:    {args.address}")
    print(f"  Decimals:   {token.get('decimals','—')}")
    print(f"  Holders:    {token.get('holders_count','—')}")
    print(f"  Price:      ${token.get('exchange_rate','—')}")
    print(f"  Market Cap: ${token.get('circulating_market_cap','—')}")
    print(f"  24h Volume: {token.get('volume_24h','—')}")
    print(f"  Supply:     {token.get('total_supply','—')}")
    print("=" * 50)


def cmd_live(client, args):
    """Live monitor — poll for new transactions."""
    print(f"\n🔴 LIVE MODE — Polling every {args.interval}s (Ctrl+C to stop)\n")
    seen = set()
    try:
        while True:
            data = client.get_latest_transactions()
            items = (data or {}).get("items", [])
            new = [t for t in items if t.get("hash") not in seen]
            for t in new:
                seen.add(t.get("hash"))
                val = BlockscoutClient.wei_to_eth(t.get("value", "0"))
                h = BlockscoutClient.format_hash
                ta = BlockscoutClient.time_ago
                frm = h((t.get("from") or {}).get("hash", ""), 8, 4)
                to_obj = t.get("to")
                to = h(to_obj.get("hash", ""), 8, 4) if isinstance(to_obj, dict) else "—"
                status = "✓" if t.get("status") == "ok" else "✗"
                types = ",".join((t.get("transaction_types") or [])[:2])
                print(f"  {status} {h(t.get('hash',''),12,6)} {frm}→{to} {val:.4f} ETH [{types}] {ta(t.get('timestamp'))}")
            if len(seen) > 500:
                seen = set(list(seen)[-200:])
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\nStopped.")


def main():
    parser = argparse.ArgumentParser(
        description="RobinhoodScan — Robinhood Chain Transaction Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py stats                         # Network stats
  python cli.py txs                           # Latest transactions
  python cli.py txs --output txs.csv          # Save to CSV
  python cli.py blocks                        # Latest blocks
  python cli.py address 0x50954d39...         # Address detail
  python cli.py token 0x0Bd7D308...           # Token detail
  python cli.py live --interval 5             # Live tx monitor
  python cli.py web                           # Launch web explorer
        """
    )
    sub = parser.add_subparsers(dest="command")

    # stats
    p_stats = sub.add_parser("stats", help="Network statistics")
    p_stats.add_argument("--output", "-o", help="Save to CSV")

    # txs
    p_txs = sub.add_parser("txs", help="Latest transactions")
    p_txs.add_argument("--limit", "-n", type=int, default=20, help="Number of results")
    p_txs.add_argument("--output", "-o", help="Save to CSV")

    # blocks
    p_blocks = sub.add_parser("blocks", help="Latest blocks")
    p_blocks.add_argument("--limit", "-n", type=int, default=20, help="Number of results")
    p_blocks.add_argument("--output", "-o", help="Save to CSV")

    # address
    p_addr = sub.add_parser("address", help="Address detail and transactions")
    p_addr.add_argument("address", help="Wallet/contract address")
    p_addr.add_argument("--limit", "-n", type=int, default=20, help="Number of txs")
    p_addr.add_argument("--output", "-o", help="Save txs to CSV")

    # token
    p_token = sub.add_parser("token", help="Token info")
    p_token.add_argument("address", help="Token contract address")

    # live
    p_live = sub.add_parser("live", help="Live transaction monitor")
    p_live.add_argument("--interval", "-i", type=int, default=10, help="Poll interval (seconds)")

    # web
    p_web = sub.add_parser("web", help="Launch web explorer")
    p_web.add_argument("--port", "-p", type=int, default=5000, help="Port")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cfg = load_config()
    api_cfg = cfg.get("api", {})
    client = BlockscoutClient(
        base_url=api_cfg.get("base_url", "https://robinhoodchain.blockscout.com"),
        api_key=api_cfg.get("api_key", ""),
        timeout=api_cfg.get("timeout", 10),
        rate_limit_delay=api_cfg.get("rate_limit_delay", 0.15),
    )

    if args.command == "stats":
        cmd_stats(client, args)
    elif args.command == "txs":
        cmd_txs(client, args)
    elif args.command == "blocks":
        cmd_blocks(client, args)
    elif args.command == "address":
        cmd_address(client, args)
    elif args.command == "token":
        cmd_token(client, args)
    elif args.command == "live":
        cmd_live(client, args)
    elif args.command == "web":
        print(f"🦝 Launching web explorer on port {args.port}...")
        import web_app
        web_app.app.run(host="0.0.0.0", port=args.port, debug=True)


if __name__ == "__main__":
    main()
