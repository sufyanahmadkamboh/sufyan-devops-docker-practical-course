"""A tiny orders service: answers every GET request on port 8080."""
from http.server import BaseHTTPRequestHandler, HTTPServer


class Orders(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"orders service ok\n")


HTTPServer(("0.0.0.0", 8080), Orders).serve_forever()
