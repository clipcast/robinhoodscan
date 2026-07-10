# RobinhoodScan 🦝

**Robinhood Chain Blockchain Explorer** — stats page clone of [robinhoodchain.blockscout.com/stats](https://robinhoodchain.blockscout.com/stats).

Deployed on Vercel. Powered by Blockscout API v2 with Pro API key.

## Live Demo
Deploy to Vercel → get instant public URL.

## Structure (Vercel)
```
robinhoodscan/
├── api/                    # Vercel serverless functions
│   ├── stats.py            # GET /api/stats
│   ├── blocks.py           # GET /api/blocks
│   └── transactions.py     # GET /api/transactions
├── public/
│   └── index.html          # Stats page (served statically)
├── api_client.py           # Blockscout API v2 client
├── vercel.json             # Vercel config + env vars
├── requirements.txt        # Python deps
├── config.yaml             # Local config
├── cli.py                  # CLI for local use
└── web_app.py              # Flask app for local dev
```

## Deploy to Vercel

### Option A: Vercel CLI
```bash
npm i -g vercel
cd robinhoodscan
vercel --prod
```

### Option B: GitHub + Vercel Dashboard
1. Push this repo to GitHub
2. Go to vercel.com → New Project → Import GitHub repo
3. Vercel auto-detects Python + `vercel.json`
4. Click Deploy → get public URL

## Local Development
```bash
pip install -r requirements.txt
python web_app.py
# → http://localhost:5000/stats
```

## CLI
```bash
python cli.py stats       # Network stats
python cli.py txs         # Latest transactions
python cli.py blocks      # Latest blocks
python cli.py live        # Live tx monitor
```

## Environment Variables
Set in Vercel dashboard or vercel.json:
- `BLOCKSCOUT_API_KEY` — Pro API key
- `BLOCKSCOUT_BASE_URL` — API endpoint

## API Endpoints
| Route | Description |
|-------|-------------|
| `/` | Stats page (HTML) |
| `/api/stats` | Network statistics (JSON) |
| `/api/blocks` | Latest blocks (JSON) |
| `/api/transactions` | Latest transactions (JSON) |
