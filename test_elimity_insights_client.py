from contextlib import contextmanager
from datetime import datetime, timezone, time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from json import loads
from os import devnull
from threading import Thread
from typing import BinaryIO, Any, Iterable
from unittest import TestCase
from zlib import decompress

from httpchunked import decode

from elimity_insights_client import (
    Client,
    Config,
    Relationship,
    Entity,
    DomainGraph,
    AttributeAssignment,
    BooleanValue,
    DateValue,
    DateTimeValue,
    NumberValue,
    StringValue,
    TimeValue,
    ConnectorLog,
    Level,
    DomainGraphSchema,
    AttributeType,
    Type,
    EntityType,
    RelationshipAttributeType,
)


class TestClient(TestCase):
    def test_create_connector_logs(self) -> None:
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
        logs_iter = iter(logs)
        with _create_client(_CreateConnectorLogsHandler) as client:
            client.create_connector_logs(logs_iter)

    def test_encode_datetime(self) -> None:
        # use pre-epoch local timestamp to trigger https://bugs.python.org/issue36759
        timestamp = datetime(1969, 1, 1)
        log = ConnectorLog(level=Level.INFO, message="", timestamp=timestamp)
        logs = [log]
        with _create_client(_EncodeDatetimeHandler) as client:
            client.create_connector_logs(logs)

    def test_get_domain_graph_schema(self) -> None:
        attribute_type = AttributeType(False, "foo", "bar", "baz", Type.STRING)
        attribute_types = [attribute_type]
        entity_type = EntityType("foo", "bar", "baz", "bax")
        entity_types = [entity_type]
        relationship_attribute_type = RelationshipAttributeType(
            True, "bar", "bax", "baz", "foo", Type.DATE_TIME
        )
        relationship_attribute_types = [relationship_attribute_type]
        expected = DomainGraphSchema(
            attribute_types, entity_types, relationship_attribute_types
        )
        with _create_client(_GetDomainGraphSchemaHandler) as client:
            actual = client.get_domain_graph_schema()
        self.assertEqual(expected, actual)

    def test_reload_domain_graph(self) -> None:
        graph = DomainGraph(
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
        with _create_client(_ReloadDomainGraphHandler) as client:
            client.reload_domain_graph(graph)


@contextmanager
def _create_client(handler_class) -> Iterable[Client]:
    server_address = "", 0
    server = HTTPServer(server_address, handler_class)
    thread = Thread(target=server.serve_forever)
    thread.start()

    base_path = f"http://localhost:{server.server_port}"
    config = Config(base_path=base_path, token="foo")
    try:
        yield Client(config)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def _decode(chunked: BinaryIO) -> Any:
    buffer = BytesIO()
    decode(buffer, chunked)
    compressed = buffer.getvalue()
    serialized = decompress(compressed)
    return loads(serialized)


class _CreateConnectorLogsHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        if self.path != "/custom-connector-logs":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

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
        actual = _decode(self.rfile)
        if expected != actual:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def log_message(self, format, *args):
        pass


class _EncodeDatetimeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        with open(devnull, "bw") as file:
            decode(file, self.rfile)

        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def log_message(self, format, *args) -> None:
        pass


class _GetDomainGraphSchemaHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        if self.path != "/domain-graph-schema":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        self.send_response(HTTPStatus.OK)
        schema = b"""{
    "entityAttributeTypes": [
        {
            "archived": false,
            "description": "foo",
            "category": "bar",
            "name": "baz",
            "type": "string"
        }
    ],
    "entityTypes": [
        {
            "icon": "foo",
            "key": "bar",
            "plural": "baz",
            "singular": "bax"
        }
    ],
    "relationshipAttributeTypes": [
        {
            "archived": true,
            "childType": "foo",
            "description": "bar",
            "name": "baz",
            "parentType": "bax",
            "type": "dateTime"
        }
    ]
}
"""
        nb_bytes = len(schema)
        content_length = str(nb_bytes)
        self.send_header("Content-Length", content_length)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(schema)

    def log_message(self, format, *args) -> None:
        pass


class _ReloadDomainGraphHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self) -> None:
        if self.path != "/custom-connector-domain-graphs":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

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
        actual = _decode(self.rfile)
        if expected != actual:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def log_message(self, format, *args) -> None:
        pass
