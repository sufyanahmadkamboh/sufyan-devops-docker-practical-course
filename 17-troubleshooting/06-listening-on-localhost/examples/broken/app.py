"""The tickets service: answers every GET request on port 8080."""
from http.server import BaseHTTPRequestHandler, HTTPServer


class Tickets(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"tickets service ok\n")


# binds to the loopback interface only: reachable from inside this container, nowhere else
HTTPServer(("127.0.0.1", 8080), Tickets).serve_forever()
