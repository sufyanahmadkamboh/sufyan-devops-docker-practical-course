"""The billing service. It needs DATABASE_URL; CURRENCY is optional."""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

DATABASE_URL = os.environ["DATABASE_URL"]          # required: fail at start if it is missing
CURRENCY = os.environ.get("CURRENCY", "EUR")       # optional, with a default


class Billing(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"billing ok, currency {CURRENCY}\n".encode())


print(f"billing: starting with database {DATABASE_URL.split('@')[-1]}", flush=True)
HTTPServer(("0.0.0.0", 8080), Billing).serve_forever()
