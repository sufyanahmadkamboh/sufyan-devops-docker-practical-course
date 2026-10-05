"""A tiny web app that records every visit in data/visits.log (Python standard library only)."""
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

os.makedirs("data", exist_ok=True)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        with open("data/visits.log", "a") as log:
            log.write(f"{datetime.now(timezone.utc).isoformat()} {self.path}\n")
        body = f"hello from uid {os.getuid()}\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body)


HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
