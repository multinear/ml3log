import http.server
import socketserver
import json
import threading
import os
import signal
import sys
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse

# Global storage for logs
_logs: List[Dict[str, Any]] = []
_logs_lock = threading.Lock()

# Get the path to the template file
_TEMPLATE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "templates"
_TEMPLATE_PATH = _TEMPLATE_DIR / "viewer.html"

# Global server instance for proper shutdown
_server = None
_server_lock = threading.Lock()
_server_started = False


def _read_template() -> str:
    """Read the HTML template from the file."""
    try:
        with open(_TEMPLATE_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to a simple template if the file is not found
        return """
        <!DOCTYPE html>
        <html>
        <head><title>ML3Log Viewer</title></head>
        <body>
            <h1>ML3Log Viewer</h1>
            <p>Template file not found. Please check your installation.</p>
        </body>
        </html>
        """


# Custom TCP Server with socket reuse
class ReuseAddressServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True  # This enables SO_REUSEADDR


class ML3LogHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/':
            self._set_headers()
            self.wfile.write(_read_template().encode())
        elif path == '/api/logs':
            self._set_headers('application/json')
            with _logs_lock:
                self.wfile.write(json.dumps(_logs).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/traces':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                log_entry = json.loads(post_data.decode('utf-8'))
                with _logs_lock:
                    _logs.append(log_entry)

                self._set_headers()
                self.wfile.write(b'{"status": "success"}')
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"status": "error", "message": "Invalid JSON"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def shutdown_server(signum=None, frame=None):
    """Properly shutdown the server when receiving a signal"""
    global _server
    if _server:
        print("\nShutting down ML3Log server...")
        _server.shutdown()
        _server.server_close()
        print("Server shutdown complete.")
    sys.exit(0)


def start_server(address: str = 'localhost', port: int = 6020) -> None:
    """
    Start the ML3Log web server on the specified port.
    If the server is already running, this function will return immediately.

    Args:
        port: The port to run the server on (default: 6020)
    """
    global _server, _server_started

    # Use a lock to ensure thread safety
    with _server_lock:
        # If server is already started, just return
        if _server_started:
            return _server

        try:
            server_address = (address, port)
            _server = ReuseAddressServer(server_address, ML3LogHandler)

            # Register signal handlers for clean shutdown
            signal.signal(signal.SIGINT, shutdown_server)  # Ctrl+C
            signal.signal(signal.SIGTERM, shutdown_server)  # Termination signal

            print(f"ML3Log server started at http://{address}:{port}")
            print("Press Ctrl+C to stop the server")

            # Run the server in a separate thread
            server_thread = threading.Thread(target=_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            # Mark as started
            _server_started = True

            return _server
        except OSError as e:
            # If the error is "Address already in use", assume another instance
            # already started the server (race condition)
            if e.errno == 48:  # Address already in use
                print(f"ML3Log server already running at http://localhost:{port}")
                _server_started = True
                return None
            else:
                # For other errors, re-raise
                raise
