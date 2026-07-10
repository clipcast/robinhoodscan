"""
Vercel Serverless Function — /api/transactions
Returns latest transactions from Robinhood Chain Blockscout API v2.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import BlockscoutClient

API_KEY = os.environ.get("BLOCKSCOUT_API_KEY", "proapi_bSfD5L1WCvobulkqOHsRehjHZwEJ5QRbh2tEgIAl5WFOFwEnP0ZjjNftJURaTQbdg_l6cgL")
BASE_URL = os.environ.get("BLOCKSCOUT_BASE_URL", "https://robinhoodchain.blockscout.com")

client = BlockscoutClient(base_url=BASE_URL, api_key=API_KEY, timeout=15, rate_limit_delay=0)


def handler(req, res):
    data = client.get_latest_transactions()
    res.setHeader("Content-Type", "application/json")
    res.setHeader("Access-Control-Allow-Origin", "*")
    res.status(200).send(json.dumps(data or {}))
