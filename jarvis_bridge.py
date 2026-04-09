"""
Jarvis Bridge Server
Reads Jarvis state + last response from temp files and serves them via HTTP.
Run this alongside Jarvis so the iCUE widget can poll status.
"""

import json
import os
import tempfile
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

STATE_FILE = os.path.join(tempfile.gettempdir(), "jarvis_state")
RESPONSE_FILE = os.path.join(tempfile.gettempdir(), "jarvis_last_response")
PORT = 9847


class BridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            state = self._read_file(STATE_FILE, "asleep")
            last_response = self._read_file(RESPONSE_FILE, "")
            try:
                mtime = os.path.getmtime(RESPONSE_FILE)
                timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(mtime))
            except OSError:
                timestamp = ""

            payload = json.dumps({
                "state": state.strip(),
                "last_response": last_response.strip(),
                "timestamp": timestamp,
            })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress request logs

    @staticmethod
    def _read_file(path, default=""):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return default


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), BridgeHandler)
    print(f"Jarvis Bridge running on http://127.0.0.1:{PORT}/status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBridge stopped.")
        server.server_close()
