from http.server import BaseHTTPRequestHandler
import json, sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_client import BlockscoutClient

API_KEY = os.environ.get("BLOCKSCOUT_API_KEY", "")
BASE_URL = os.environ.get("BLOCKSCOUT_BASE_URL", "https://robinhoodchain.blockscout.com")
client = BlockscoutClient(base_url=BASE_URL, api_key=API_KEY, timeout=15, rate_limit_delay=0)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = client.get_latest_transactions()
        body = json.dumps(data or {}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)
