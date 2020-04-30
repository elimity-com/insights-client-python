from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest import TestCase

from insights_client.client import Config, Client, ConnectorLog, Level


class TestMarshalDateTime(TestCase):
    def test_marshal_datetime(self):
        server_address = "", 0
        server = HTTPServer(server_address, _Handler)
        thread = Thread(target=server.serve_forever)
        thread.start()

        url = f"http://localhost:{server.server_port}"
        config = Config(token="foo", url=url, debug=False)
        client = Client(config=config, disable_ssl_check=True)

        # use pre-epoch local timestamp to trigger https://bugs.python.org/issue36759
        timestamp = datetime(1969, 1, 1)
        log = ConnectorLog(level=Level.INFO, message="", timestamp=timestamp)
        logs = [log]
        client.create_connector_logs(logs)

        server.shutdown()
        server.server_close()
        thread.join()


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Length", 0)
        self.end_headers()

    def log_message(self, format, *args):
        pass
