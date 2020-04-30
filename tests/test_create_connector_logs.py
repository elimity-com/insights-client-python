from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads
from threading import Thread
from unittest import TestCase

from insights_client.client import Config, Client, ConnectorLog, Level


class TestCreateConnectorLogs(TestCase):
    def test_create_connector_logs(self):
        server_address = "", 0
        server = HTTPServer(server_address, _Handler)
        thread = Thread(target=server.serve_forever)
        thread.start()

        url = f"http://localhost:{server.server_port}"
        config = Config(token="foo", url=url, debug=False)
        client = Client(config=config, disable_ssl_check=True)

        logs = [
            ConnectorLog(
                level=Level.INFO,
                message="Happy New Year!",
                timestamp=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ),
            ConnectorLog(
                level=Level.ALERT,
                message="Spooky...",
                timestamp=datetime(2020, 10, 31, 23, 55, tzinfo=timezone.utc),
            ),
        ]
        client.create_connector_logs(logs)

        server.shutdown()
        server.server_close()
        thread.join()


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length_str = self.headers["Content-Length"]
        content_length = int(content_length_str)
        buffer = bytearray()

        while content_length > 0:
            chunk = self.rfile.read(content_length)
            content_length -= len(chunk)
            buffer.extend(chunk)

        expected = [
            {
                "level": "info",
                "message": "Happy New Year!",
                "timestamp": "2020-01-01T00:00:00+00:00",
            },
            {
                "level": "alert",
                "message": "Spooky...",
                "timestamp": "2020-10-31T23:55:00+00:00",
            },
        ]
        actual = loads(buffer)
        status = HTTPStatus.OK if expected == actual else HTTPStatus.BAD_REQUEST
        self.send_response(status)
        self.send_header("Content-Length", 0)
        self.end_headers()

    def log_message(self, format, *args):
        pass
