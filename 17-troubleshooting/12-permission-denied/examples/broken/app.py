"""The reports service: reads its settings at start-up, then answers on port 8080."""
import configparser
from http.server import BaseHTTPRequestHandler, HTTPServer

settings = configparser.ConfigParser()
with open("settings.ini") as f:                     # raises PermissionError if the file is not readable
    settings.read_file(f)
TITLE = settings["reports"]["title"]


class Reports(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"{TITLE}: ok\n".encode())


print(f"reports: settings loaded ({TITLE})", flush=True)
HTTPServer(("0.0.0.0", 8080), Reports).serve_forever()
