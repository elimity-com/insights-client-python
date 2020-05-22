from datetime import time, timezone, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from json import loads
from threading import Thread
from unittest import TestCase
from zlib import decompress

from httpchunked import decode

from insights_client.client import (
    Config,
    Client,
    Relationship,
    AttributeAssignment,
    TimeValue,
    Entity,
    StringValue,
    NumberValue,
    DateTimeValue,
    DateValue,
    BooleanValue,
    DomainGraph,
)


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self):
        expected = {
            "entities": [
                {
                    "active": True,
                    "attributeAssignments": [
                        {
                            "attributeTypeName": "foo",
                            "value": {"type": "boolean", "value": "true"},
                        },
                        {
                            "attributeTypeName": "bar",
                            "value": {"type": "date", "value": "2006-01-02"},
                        },
                        {
                            "attributeTypeName": "baq",
                            "value": {
                                "type": "dateTime",
                                "value": "2006-01-02T12:04:05+00:00",
                            },
                        },
                        {
                            "attributeTypeName": "baw",
                            "value": {"type": "number", "value": "99"},
                        },
                        {
                            "attributeTypeName": "bae",
                            "value": {"type": "string", "value": "bae string"},
                        },
                    ],
                    "id": "foo",
                    "name": "bar",
                    "type": "baz",
                },
                {
                    "active": False,
                    "attributeAssignments": [
                        {
                            "attributeTypeName": "baz",
                            "value": {"type": "time", "value": "15:04:05Z"},
                        }
                    ],
                    "id": "bar",
                    "name": "baz",
                    "type": "foo",
                },
            ],
            "relationships": [
                {
                    "attributeAssignments": [
                        {
                            "attributeTypeName": "foo",
                            "value": {"type": "string", "value": "bar"},
                        }
                    ],
                    "fromId": "foo",
                    "fromType": "baz",
                    "toId": "bar",
                    "toType": "foo",
                }
            ],
            "historyTimestamp": "2001-02-03T04:05:06+00:00",
        }

        buffer = BytesIO()
        decode(buffer, self.rfile)
        raw = buffer.getvalue()
        decompressed = decompress(raw)
        actual = loads(decompressed)

        status = HTTPStatus.OK if expected == actual else HTTPStatus.BAD_REQUEST
        self.send_response(status)
        self.send_header("Content-Length", 0)
        self.end_headers()

    def log_message(self, format, *args):
        pass


class TestReloadDomainGraph(TestCase):
    def test_reload_domain_graph(self):
        server_address = "", 0
        server = HTTPServer(server_address, _Handler)
        thread = Thread(target=server.serve_forever)
        thread.start()

        url = f"http://localhost:{server.server_port}"
        config = Config(token="foo", url=url, debug=False)
        client = Client(config=config, disable_ssl_check=True)

        domain_graph = DomainGraph(
            entities=[
                Entity(
                    active=True,
                    attribute_assignments=[
                        AttributeAssignment(
                            attribute_type_name="foo", value=BooleanValue(True)
                        ),
                        AttributeAssignment(
                            attribute_type_name="bar",
                            value=DateValue(datetime(2006, 1, 2)),
                        ),
                        AttributeAssignment(
                            attribute_type_name="baq",
                            value=DateTimeValue(
                                datetime(2006, 1, 2, 12, 4, 5, tzinfo=timezone.utc)
                            ),
                        ),
                        AttributeAssignment(
                            attribute_type_name="baw", value=NumberValue(99)
                        ),
                        AttributeAssignment(
                            attribute_type_name="bae", value=StringValue("bae string")
                        ),
                    ],
                    id="foo",
                    name="bar",
                    type="baz",
                ),
                Entity(
                    active=False,
                    attribute_assignments=[
                        AttributeAssignment(
                            attribute_type_name="baz",
                            value=TimeValue(time(15, 4, 5, tzinfo=timezone.utc)),
                        )
                    ],
                    id="bar",
                    name="baz",
                    type="foo",
                ),
            ],
            relationships=[
                Relationship(
                    attribute_assignments=[
                        AttributeAssignment(
                            attribute_type_name="foo", value=StringValue("bar")
                        ),
                    ],
                    from_entity_id="foo",
                    from_entity_type="baz",
                    to_entity_id="bar",
                    to_entity_type="foo",
                )
            ],
            timestamp=datetime(2001, 2, 3, 4, 5, 6, tzinfo=timezone.utc),
        )

        client.reload_domain_graph(domain_graph)
        server.shutdown()
        server.server_close()
        thread.join()
