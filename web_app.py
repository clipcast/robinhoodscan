"""
RobinhoodScan — Robinhood Chain Stats Explorer
================================================
Clone of robinhoodchain.blockscout.com/stats
Single-page Flask app showing live network statistics.
"""
from flask import Flask, jsonify
from api_client import BlockscoutClient
import yaml

app = Flask(__name__)

def load_config():
    try:
        with open("config.yaml") as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

cfg = load_config()
api_cfg = cfg.get("api", {})
client = BlockscoutClient(
    base_url=api_cfg.get("base_url", "https://robinhoodchain.blockscout.com"),
    api_key=api_cfg.get("api_key", ""),
    timeout=api_cfg.get("timeout", 15),
    rate_limit_delay=api_cfg.get("rate_limit_delay", 0.15),
)

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Robinhood Chain stats — RobinhoodScan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0d0d0f;
  --panel: #16171a;
  --border: #2a2b2f;
  --border-light: #202124;
  --text: #f2f2f2;
  --text-secondary: #9a9ba0;
  --muted: #6b6c72;
  --link: #D4FF00;
  --green: #00e6a8;
  --green-bg: rgba(0,230,168,0.12);
  --red: #ff5c5c;
  --red-bg: rgba(255,92,92,0.12);
  --hero: #D4FF00;
  --hero-dark: #0d0d0f;
  --purple: #c9b8ff;
  --orange: #ffcf6e;
  --blue-bg: rgba(212,255,0,0.08);
  --blue: #D4FF00;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',system-ui,sans-serif; background:var(--bg); color:var(--text); font-size:14px; }

/* Navbar */
.navbar { background:var(--panel); border-bottom:1px solid var(--border); padding:10px 0; position:sticky; top:0; z-index:100; }
.nav-inner { max-width:1200px; margin:0 auto; display:flex; align-items:center; gap:20px; padding:0 20px; }
.nav-logo { font-size:16px; font-weight:800; display:flex; align-items:center; gap:8px; color:var(--text); text-decoration:none; }
.nav-logo .dot { width:30px; height:30px; background:var(--hero); border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:18px; }
.nav-logo .chain-name { font-weight:600; font-size:13px; color:var(--text-secondary); }
.nav-links { display:flex; gap:16px; flex:1; margin-left:12px; }
.nav-links a { color:var(--text-secondary); font-size:13px; font-weight:500; text-decoration:none; }
.nav-links a:hover { color:var(--text); }
.nav-links a.active { color:var(--hero); font-weight:600; }
.nav-search { display:flex; align-items:center; }
.nav-search input { width:300px; padding:8px 14px; border:1px solid var(--border); border-radius:8px; font-size:13px; outline:none; font-family:inherit; background:var(--bg); color:var(--text); }
.nav-search input::placeholder { color:var(--muted); }
.nav-search input:focus { border-color:var(--link); box-shadow:0 0 0 2px rgba(212,255,0,0.15); }

/* Container */
.container { max-width:1200px; margin:0 auto; padding:24px 20px; }

/* Page title */
.page-title { font-size:24px; font-weight:800; margin-bottom:4px; }
.page-sub { font-size:13px; color:var(--text-secondary); margin-bottom:24px; display:flex; align-items:center; gap:8px; }
.live-dot { width:8px; height:8px; background:var(--green); border-radius:50%; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* Stats grid */
.stats-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; margin-bottom:32px; }
.stat-card { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:18px 20px; transition:box-shadow .2s, border-color .2s; }
.stat-card:hover { box-shadow:0 2px 12px rgba(212,255,0,0.06); border-color:#3a3b40; }
.stat-card .icon { width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:18px; margin-bottom:10px; background:var(--blue-bg); }
.stat-card .icon.blue { background:var(--blue-bg); }
.stat-card .icon.green { background:var(--green-bg); }
.stat-card .icon.orange { background:rgba(255,207,110,0.1); }
.stat-card .icon.purple { background:rgba(201,184,255,0.1); }
.stat-card .label { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.6px; font-weight:600; }
.stat-card .value { font-size:22px; font-weight:700; margin-top:4px; font-family:'JetBrains Mono',monospace; color:var(--text); }
.stat-card .value.green { color:var(--green); }
.stat-card .value.red { color:var(--red); }
.stat-card .sub { font-size:11px; color:var(--muted); margin-top:3px; }

/* Section */
.section { margin-bottom:32px; }
.section-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.section-header h2 { font-size:16px; font-weight:700; }
.section-header a { font-size:12px; color:var(--link); text-decoration:none; }

/* Panel */
.panel { background:var(--panel); border:1px solid var(--border); border-radius:12px; overflow:hidden; margin-bottom:16px; }
.panel-header { padding:14px 20px; border-bottom:1px solid var(--border-light); font-size:14px; font-weight:600; display:flex; align-items:center; }
.panel-header .badge-count { margin-left:auto; font-size:12px; color:var(--muted); font-weight:400; }

/* Table */
table { width:100%; border-collapse:collapse; }
th { text-align:left; padding:10px 16px; font-size:11px; text-transform:uppercase; color:var(--muted); border-bottom:1px solid var(--border-light); background:var(--border-light); font-weight:600; letter-spacing:.4px; white-space:nowrap; }
td { padding:10px 16px; border-bottom:1px solid var(--border-light); font-size:13px; white-space:nowrap; color:var(--text); }
tr:last-child td { border-bottom:none; }
tr:hover td { background:rgba(212,255,0,0.03); }
.mono { font-family:'JetBrains Mono',Monaco,Consolas,monospace; font-size:12px; }

/* Badges */
.badge { display:inline-block; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:600; }
.badge-ok { background:var(--green-bg); color:var(--green); }
.badge-err { background:var(--red-bg); color:var(--red); }
.badge-type { background:var(--blue-bg); color:var(--blue); }
.badge-coin { background:rgba(255,207,110,0.1); color:var(--orange); }

/* Two column layout */
.two-col { display:grid; grid-template-columns:1.4fr 1fr; gap:16px; }

/* Footer */
.footer { text-align:center; padding:24px; color:var(--muted); font-size:12px; border-top:1px solid var(--border); margin-top:32px; }

/* Gas gauge */
.gas-gauge { display:flex; gap:8px; align-items:center; }
.gas-bar { width:120px; height:6px; background:var(--border-light); border-radius:3px; overflow:hidden; }
.gas-bar .fill { height:100%; border-radius:3px; }
.gas-bar .fill.slow { background:var(--green); width:33%; }
.gas-bar .fill.avg { background:var(--orange); width:66%; }
.gas-bar .fill.fast { background:var(--red); width:100%; }

/* Spinner */
.spinner { display:inline-block; width:14px; height:14px; border:2px solid var(--border); border-top-color:var(--hero); border-radius:50%; animation:spin .8s linear infinite; }
@keyframes spin { to{transform:rotate(360deg)} }

/* Responsive */
@media (max-width:768px) {
  .two-col { grid-template-columns:1fr; }
  .nav-search input { width:160px; }
  .stats-grid { grid-template-columns:1fr 1fr; }
}
</style>
</head>
<body>

<div class="navbar">
  <div class="nav-inner">
    <a href="/" class="nav-logo">
      <span class="dot">🪶</span>
      <span>RobinhoodScan</span>
      <span class="chain-name">| Robinhood Chain</span>
    </a>
    <nav class="nav-links">
      <a href="/">Home</a>
      <a href="/txs">Transactions</a>
      <a href="/blocks">Blocks</a>
      <a href="/tokens">Tokens</a>
      <a href="/stats" class="active">Stats</a>
    </nav>
    <form class="nav-search" action="/search" method="get">
      <input type="text" name="q" placeholder="Search address / tx / block...">
    </form>
  </div>
</div>

<div class="container">
  <div class="page-title">Network Stats</div>
  <div class="page-sub"><span class="live-dot"></span> Live data from Robinhood Chain — updated every 30s</div>

  <!-- Overview Cards -->
  <div class="stats-grid" id="overviewCards">
    <div class="stat-card">
      <div class="icon blue">⛏️</div>
      <div class="label">Latest Block</div>
      <div class="value" id="totalBlocks">—</div>
      <div class="sub" id="totalBlocksSub">blocks</div>
    </div>
    <div class="stat-card">
      <div class="icon green">📝</div>
      <div class="label">Total Transactions</div>
      <div class="value" id="totalTxs">—</div>
      <div class="sub" id="totalTxsSub">transactions</div>
    </div>
    <div class="stat-card">
      <div class="icon purple">👥</div>
      <div class="label">Total Addresses</div>
      <div class="value" id="totalAddrs">—</div>
      <div class="sub" id="totalAddrsSub">addresses</div>
    </div>
    <div class="stat-card">
      <div class="icon orange">⚡</div>
      <div class="label">Transactions Today</div>
      <div class="value" id="txsToday">—</div>
      <div class="sub" id="txsTodaySub">in last 24h</div>
    </div>
    <div class="stat-card">
      <div class="icon green">💰</div>
      <div class="label">ETH Price</div>
      <div class="value green" id="ethPrice">—</div>
      <div class="sub" id="ethPriceSub">market cap: —</div>
    </div>
    <div class="stat-card">
      <div class="icon blue">⏱️</div>
      <div class="label">Avg Block Time</div>
      <div class="value" id="blockTime">—</div>
      <div class="sub" id="blockTimeSub">seconds</div>
    </div>
    <div class="stat-card">
      <div class="icon orange">⛽</div>
      <div class="label">Gas Tracker</div>
      <div class="value" id="gasFast">—</div>
      <div class="sub" id="gasSub">slow: — / avg: — Gwei</div>
    </div>
    <div class="stat-card">
      <div class="icon purple">📊</div>
      <div class="label">Gas Used Today</div>
      <div class="value" id="gasToday">—</div>
      <div class="sub" id="gasTodaySub">network util: —</div>
    </div>
  </div>

  <!-- Latest Blocks + Transactions -->
  <div class="two-col">
    <div class="section">
      <div class="section-header">
        <h2>Latest Blocks</h2>
        <a href="/blocks">View all →</a>
      </div>
      <div class="panel">
        <table>
          <thead><tr><th>Block</th><th>Age</th><th>Gas Used</th><th>Size</th><th>Base Fee</th></tr></thead>
          <tbody id="blocksBody">
            <tr><td colspan="5" style="text-align:center;color:var(--muted);padding:20px"><span class="spinner"></span> Loading...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="section">
      <div class="section-header">
        <h2>Latest Transactions</h2>
        <a href="/txs">View all →</a>
      </div>
      <div class="panel">
        <table>
          <thead><tr><th>Hash</th><th>From</th><th>Value</th><th>Status</th><th>Age</th></tr></thead>
          <tbody id="txsBody">
            <tr><td colspan="5" style="text-align:center;color:var(--muted);padding:20px"><span class="spinner"></span> Loading...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Gas Prices Detail -->
  <div class="section">
    <div class="section-header"><h2>Gas Prices</h2></div>
    <div class="panel">
      <div style="padding:20px;display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
        <div>
          <div style="font-size:12px;color:var(--muted);text-transform:uppercase;font-weight:600;margin-bottom:8px">Slow</div>
          <div style="font-size:20px;font-weight:700;font-family:'JetBrains Mono',monospace" id="gasSlowVal">—</div>
          <div style="margin-top:8px"><div class="gas-gauge"><div class="gas-bar"><div class="fill slow"></div></div></div></div>
        </div>
        <div>
          <div style="font-size:12px;color:var(--muted);text-transform:uppercase;font-weight:600;margin-bottom:8px">Average</div>
          <div style="font-size:20px;font-weight:700;font-family:'JetBrains Mono',monospace" id="gasAvgVal">—</div>
          <div style="margin-top:8px"><div class="gas-gauge"><div class="gas-bar"><div class="fill avg"></div></div></div></div>
        </div>
        <div>
          <div style="font-size:12px;color:var(--muted);text-transform:uppercase;font-weight:600;margin-bottom:8px">Fast</div>
          <div style="font-size:20px;font-weight:700;font-family:'JetBrains Mono',monospace;color:var(--red)" id="gasFastVal">—</div>
          <div style="margin-top:8px"><div class="gas-gauge"><div class="gas-bar"><div class="fill fast"></div></div></div></div>
        </div>
      </div>
    </div>
  </div>

</div>

<div class="footer">
  RobinhoodScan — Robinhood Chain Explorer · Powered by Blockscout API v2 · Data may be delayed
</div>

<script>
function fmtNum(n) { return Number(n).toLocaleString(); }
function weiToEth(w) { return (Number(w) / 1e18).toFixed(4); }
function timeAgo(iso) {
  if (!iso) return '—';
  let d = new Date(iso), now = new Date(), diff = Math.floor((now - d) / 1000);
  if (diff < 60) return diff + 's ago';
  if (diff < 3600) return Math.floor(diff/60) + 'm ago';
  if (diff < 86400) return Math.floor(diff/3600) + 'h ago';
  return Math.floor(diff/86400) + 'd ago';
}
function shortHash(h, p=8, s=4) { return h ? h.slice(0,p) + '...' + h.slice(-s) : '—'; }

async function loadData() {
  try {
    // Stats
    let r = await fetch('/api/stats'); let s = await r.json();
    document.getElementById('totalBlocks').textContent = '#' + fmtNum(s.total_blocks);
    document.getElementById('totalBlocksSub').textContent = fmtNum(s.total_blocks) + ' blocks';
    document.getElementById('totalTxs').textContent = fmtNum(s.total_transactions);
    document.getElementById('totalTxsSub').textContent = fmtNum(s.total_transactions) + ' transactions';
    document.getElementById('totalAddrs').textContent = fmtNum(s.total_addresses);
    document.getElementById('totalAddrsSub').textContent = fmtNum(s.total_addresses) + ' addresses';
    document.getElementById('txsToday').textContent = fmtNum(s.transactions_today);
    document.getElementById('txsTodaySub').textContent = 'in last 24h';
    document.getElementById('ethPrice').textContent = '$' + Number(s.coin_price).toLocaleString();
    document.getElementById('ethPriceSub').textContent = 'market cap: $' + Number(s.market_cap).toLocaleString(undefined,{maximumFractionDigits:0});
    document.getElementById('blockTime').textContent = s.average_block_time + 's';
    document.getElementById('blockTimeSub').textContent = 'seconds per block';
    let gp = s.gas_prices || {};
    document.getElementById('gasFast').textContent = gp.fast + ' Gwei';
    document.getElementById('gasSub').textContent = 'slow: ' + gp.slow + ' / avg: ' + gp.average + ' Gwei';
    document.getElementById('gasToday').textContent = fmtNum(Number(s.gas_used_today));
    document.getElementById('gasTodaySub').textContent = 'network util: ' + (s.network_utilization_percentage || 0).toExponential(2) + '%';
    document.getElementById('gasSlowVal').textContent = gp.slow + ' Gwei';
    document.getElementById('gasAvgVal').textContent = gp.average + ' Gwei';
    document.getElementById('gasFastVal').textContent = gp.fast + ' Gwei';
  } catch(e) { console.error('stats error', e); }

  try {
    // Blocks
    let r = await fetch('/api/blocks'); let d = await r.json();
    let items = (d.items || []).slice(0, 8);
    document.getElementById('blocksBody').innerHTML = items.map(b => `
      <tr>
        <td><a href="/block/${b.height}" style="color:var(--link);text-decoration:none;font-weight:600">#${b.height}</a></td>
        <td>${timeAgo(b.timestamp)}</td>
        <td>${fmtNum(Number(b.gas_used))}</td>
        <td>${b.size || '—'} B</td>
        <td class="mono">${b.base_fee_per_gas || '—'}</td>
      </tr>`).join('');
  } catch(e) { console.error('blocks error', e); }

  try {
    // Transactions
    let r = await fetch('/api/transactions'); let d = await r.json();
    let items = (d.items || []).slice(0, 10);
    document.getElementById('txsBody').innerHTML = items.map(t => {
      let from = t.from ? t.from.hash : '';
      let to = t.to ? t.to.hash : '';
      let badge = t.status === 'ok' ? '<span class="badge badge-ok">OK</span>' : '<span class="badge badge-err">FAIL</span>';
      return `<tr>
        <td class="mono"><a href="/tx/${t.hash}" style="color:var(--link);text-decoration:none">${shortHash(t.hash,10,4)}</a></td>
        <td class="mono"><a href="/address/${from}" style="color:var(--link);text-decoration:none">${shortHash(from,4,3)}</a></td>
        <td>${weiToEth(t.value)}</td>
        <td>${badge}</td>
        <td>${timeAgo(t.timestamp)}</td>
      </tr>`;
    }).join('');
  } catch(e) { console.error('txs error', e); }
}

loadData();
setInterval(loadData, 30000);
</script>
</body>
</html>
"""


@app.route("/stats")
@app.route("/")
def stats_page():
    return PAGE


@app.route("/txs")
@app.route("/blocks")
@app.route("/tokens")
def other_pages():
    return PAGE


@app.route("/api/stats")
def api_stats():
    data = client.get_stats()
    return jsonify(data or {})


@app.route("/api/blocks")
def api_blocks():
    data = client.get_latest_blocks()
    return jsonify(data or {})


@app.route("/api/transactions")
def api_transactions():
    data = client.get_latest_transactions()
    return jsonify(data or {})


if __name__ == "__main__":
    port = cfg.get("output", {}).get("web_port", 5000)
    print(f"🦝 RobinhoodScan Stats — http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
