"""A small API with a bug: GET /report never finishes (it waits forever for a slow dependency)."""
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/report":
            time.sleep(3600)  # the bug: waits forever, no timeout
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok\n")

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


# one request at a time: a request that never finishes blocks every other request
HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
