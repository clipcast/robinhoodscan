"""
RobinhoodScan — Blockscout API v2 Client
========================================
Wraps the Robinhood Chain Blockscout API with caching, retries, and error handling.
"""
import requests
import time
import threading
from functools import lru_cache


class BlockscoutClient:
    """Client for Blockscout API v2 — Robinhood Chain."""

    def __init__(self, base_url="https://robinhoodchain.blockscout.com",
                 api_key="", timeout=15, rate_limit_delay=0.15):
        self.base_url = base_url.rstrip("/")
        self.api_base = f"{self.base_url}/api/v2"
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        headers = {"Accept": "application/json", "User-Agent": "RobinhoodScan/1.0"}
        if api_key:
            # Blockscout Pro API uses x-api-key header
            headers["x-api-key"] = api_key
        self.session.headers.update(headers)
        self._last_request = 0
        self._lock = threading.Lock()

    def _throttle(self):
        with self._lock:
            elapsed = time.time() - self._last_request
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
            self._last_request = time.time()

    def get(self, path, params=None, retries=3):
        """GET with retry and throttling. Returns dict or None on error."""
        url = f"{self.api_base}{path}" if path.startswith("/") else f"{self.api_base}/{path}"
        for attempt in range(retries + 1):
            self._throttle()
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 404:
                    return None
                if resp.status_code == 429:
                    time.sleep(2 * (attempt + 1))
                    continue
                # 500/502/503 — retry with backoff
                if resp.status_code >= 500 and attempt < retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
            except requests.RequestException:
                if attempt < retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
            break
        return None

    # ── Stats ──────────────────────────────────────────────

    def get_stats(self):
        """Network statistics."""
        return self.get("/stats")

    # ── Transactions ───────────────────────────────────────

    def get_latest_transactions(self, page_params=None):
        """Latest transactions. Pass next_page_params for pagination."""
        params = page_params or {}
        return self.get("/transactions", params=params)

    def get_transaction(self, tx_hash):
        """Single transaction detail."""
        return self.get(f"/transactions/{tx_hash}")

    def get_address_transactions(self, address, page_params=None):
        """Transactions for a specific address."""
        params = page_params or {}
        return self.get(f"/addresses/{address}/transactions", params=params)

    def get_transaction_internal_txs(self, tx_hash):
        """Internal transactions (calls) within a tx."""
        return self.get(f"/transactions/{tx_hash}/internal-transactions")

    # ── Blocks ─────────────────────────────────────────────

    def get_latest_blocks(self, page_params=None):
        """Latest blocks."""
        params = page_params or {}
        params.setdefault("type", "block")
        return self.get("/blocks", params=params)

    def get_block(self, height):
        """Single block detail."""
        return self.get(f"/blocks/{height}")

    def get_block_transactions(self, height, page_params=None):
        """Transactions in a specific block."""
        params = page_params or {}
        return self.get(f"/blocks/{height}/transactions", params=params)

    # ── Addresses ──────────────────────────────────────────

    def get_address(self, address):
        """Address info (balance, tx count, etc.)."""
        return self.get(f"/addresses/{address}")

    def get_address_token_holdings(self, address):
        """Token holdings for an address."""
        return self.get(f"/addresses/{address}/token-balances")

    # ── Tokens ─────────────────────────────────────────────

    def get_tokens(self, token_type="ERC-20", page_params=None):
        """List tokens on the chain."""
        params = page_params or {}
        params["type"] = token_type
        return self.get("/tokens", params=params)

    def get_token(self, address):
        """Token detail."""
        return self.get(f"/tokens/{address}")

    def get_token_holders(self, address, page_params=None):
        """Token holders."""
        params = page_params or {}
        return self.get(f"/tokens/{address}/holders", params=params)

    def get_token_transfers(self, address, page_params=None):
        """Token transfers for a specific token."""
        params = page_params or {}
        return self.get(f"/tokens/{address}/transfers", params=params)

    # ── Search ─────────────────────────────────────────────

    def search(self, query):
        """Search by address, tx hash, block number, or token."""
        return self.get("/search", params={"q": query})

    # ── Helpers ────────────────────────────────────────────

    @staticmethod
    def wei_to_eth(wei_str):
        """Convert wei string to ETH float."""
        try:
            return int(wei_str) / 1e18
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def format_hash(hash_str, prefix=10, suffix=6):
        """Truncate a hash for display: 0x1234...5678."""
        if not hash_str or len(hash_str) <= prefix + suffix + 3:
            return hash_str or ""
        return f"{hash_str[:prefix]}...{hash_str[-suffix:]}"

    @staticmethod
    def time_ago(iso_ts):
        """Human-readable 'x seconds/minutes ago' from ISO timestamp."""
        if not iso_ts:
            return "—"
        try:
            from datetime import datetime, timezone
            ts = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            diff = int((now - ts).total_seconds())
            if diff < 60:
                return f"{diff}s ago"
            elif diff < 3600:
                return f"{diff // 60}m ago"
            elif diff < 86400:
                return f"{diff // 3600}h ago"
            else:
                return f"{diff // 86400}d ago"
        except Exception:
            return iso_ts

    @staticmethod
    def gas_to_gwei(gas_str):
        """Convert gas price (wei) to Gwei."""
        try:
            return round(int(gas_str) / 1e9, 2)
        except (ValueError, TypeError):
            return 0.0
