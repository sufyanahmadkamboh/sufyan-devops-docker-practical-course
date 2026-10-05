"""The uploads service: records every request in data/visits.log and reports the count."""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

LOG = os.path.join("data", "visits.log")


def record() -> int:
    with open(LOG, "a") as f:                       # fails if the directory is not writable
        f.write("visit\n")
    with open(LOG) as f:
        return len(f.readlines())


class Uploads(BaseHTTPRequestHandler):
    def do_GET(self):
        count = record()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"uploads ok, {count} visits recorded\n".encode())


record()                                            # check at start-up that the data directory is writable
print("uploads: data directory is writable", flush=True)
HTTPServer(("0.0.0.0", 8080), Uploads).serve_forever()
