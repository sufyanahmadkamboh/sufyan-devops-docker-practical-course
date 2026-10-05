"""The tickets service: answers every GET request on port 8080."""
from http.server import BaseHTTPRequestHandler, HTTPServer


class Tickets(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"tickets service ok\n")


# binds to every interface of the container, so published ports reach it
HTTPServer(("0.0.0.0", 8080), Tickets).serve_forever()
