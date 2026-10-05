"""The menu API: GET /health answers ok, everything else returns the menu."""
from http.server import BaseHTTPRequestHandler, HTTPServer


class Menu(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"ok\n" if self.path == "/health" else b"espresso, cappuccino, flat white\n"
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):                   # keep the health checks out of the logs
        pass


HTTPServer(("0.0.0.0", 8080), Menu).serve_forever()
