from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from itertools import chain
from typing import Dict, Iterable, Optional, Tuple, Union
from zlib import compressobj

from requests import Response, request

from elimity_insights_client._decode_domain_graph_schema import (
    decode_domain_graph_schema,
)
from elimity_insights_client._domain_graph_schema import DomainGraphSchema
from elimity_insights_client._util import encode_datetime, encoder


@dataclass
class AttributeAssignment:
    """Assignment of a value for an attribute type."""

    attribute_type_id: str
    value: "Value"


@dataclass
class BooleanValue:
    """Value to assign for a boolean attribute type."""

    value: bool


@dataclass
class Certificate:
    """Client side certificate for mTLS connections."""

    certificate_path: str
    private_key_path: str


class Client:
    """Client for connector interactions with an Elimity Insights server."""

    def __init__(self, config: "Config") -> None:
        """Return a new client with the given configuration."""
        self._config = config

    def create_connector_logs(self, logs: Iterable["ConnectorLog"]) -> None:
        """Create connector logs."""
        json = map(_encode_connector_log, logs)
        json_string = encoder.encode(json)
        json_bytes = json_string.encode()
        self._post("application/json", json_bytes, "connector-logs")

    def get_domain_graph_schema(self) -> "DomainGraphSchema":
        """Retrieve the domain graph schema."""
        headers: Dict[str, str] = {}
        response = self._request(None, headers, "GET", "domain-graph-schema")
        json = response.json()
        return decode_domain_graph_schema(json)

    def reload_domain_graph(self, graph: "DomainGraph") -> None:
        """
        Reload a domain graph.

        This method serializes the given domain graph by streaming its entities
        and relationships to a compressed buffer. It always exhausts the given
        domain graph's entities before iterating its relationships.
        """
        json = _encode_domain_graph(graph)
        json_bytes_chunks = _compress_domain_graph(json)
        json_bytes_iter = chain.from_iterable(json_bytes_chunks)
        json_bytes = bytes(json_bytes_iter)
        self._post("application/octet-stream", json_bytes, "snapshots")

    def _post(self, content_type: str, data: bytes, path: str) -> None:
        headers = {"Content-Type": content_type}
        self._request(data, headers, "POST", path)

    def _request(
        self,
        data: Optional[bytes],
        headers: Dict[str, str],
        method: str,
        path: str,
    ) -> Response:
        config = self._config
        id_ = config.id
        url = f"{config.url}/api/custom-sources/{id_}/{path}"
        auth = str(id_), config.token
        cert = _cert(config.certificate)
        response = request(
            method,
            url,
            auth=auth,
            cert=cert,
            data=data,
            headers=headers,
            verify=config.verify_ssl,
        )
        response.raise_for_status()
        return response


@dataclass
class Config:
    """Configuration for an Elimity Insights client."""

    id: int
    url: str
    token: str
    verify_ssl: bool = True
    certificate: Optional[Certificate] = None


@dataclass
class ConnectorLog:
    """Log line produced by an Elimity Insights connector."""

    level: "Level"
    message: str
    timestamp: datetime


@dataclass
class DateTime:
    """Date-time in UTC."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int


@dataclass
class DateTimeValue:
    """Value to assign for a date-time attribute type, in UTC."""

    value: DateTime


@dataclass
class DateValue:
    """Value to assign for a date attribute type."""

    year: int
    month: int
    day: int


@dataclass
class DomainGraph:
    """Snapshot of a complete domain graph at a specific timestamp."""

    entities: Iterable["Entity"]
    relationships: Iterable["Relationship"]
    timestamp: Optional[DateTime] = None


@dataclass
class Entity:
    """Entity of a specific type, including attribute assignments."""

    attribute_assignments: Iterable[AttributeAssignment]
    id: str
    name: str
    type: str


class Level(Enum):
    """Severity level of an Elimity Insights connector log line."""

    ALERT = auto()
    INFO = auto()


@dataclass
class NumberValue:
    """Value to assign for a number attribute type."""

    value: float


@dataclass
class Relationship:
    """Relationship between two entities, including attribute assignments."""

    attribute_assignments: Iterable[AttributeAssignment]
    from_entity_id: str
    from_entity_type: str
    to_entity_id: str
    to_entity_type: str


@dataclass
class StringValue:
    """Value to assign for a string attribute type."""

    value: str


@dataclass
class TimeValue:
    """Value to assign for a time attribute type, in UTC."""

    hour: int
    minute: int
    second: int


Value = Union[
    BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue
]


def _cert(certificate: Optional[Certificate]) -> Optional[Tuple[str, str]]:
    if certificate is None:
        return None
    else:
        return certificate.certificate_path, certificate.private_key_path


def _compress_domain_graph(json: object) -> Iterable[bytes]:
    compress = compressobj()
    for json_string_chunk in encoder.iterencode(json, False):
        json_bytes_chunk = json_string_chunk.encode()
        yield compress.compress(json_bytes_chunk)
    yield compress.flush()


def _encode_attribute_assignment(assignment: AttributeAssignment) -> object:
    value = _encode_value(assignment.value)
    return {
        "attributeTypeId": assignment.attribute_type_id,
        "value": value,
    }


def _encode_connector_log(log: ConnectorLog) -> object:
    level = _encode_level(log.level)
    timestamp = encode_datetime(log.timestamp)
    return {
        "level": level,
        "message": log.message,
        "timestamp": timestamp,
    }


def _encode_date(year: int, month: int, day: int) -> object:
    return {"year": year, "month": month, "day": day}


def _encode_date_time(time: DateTime) -> object:
    return {
        "year": time.year,
        "month": time.month,
        "day": time.day,
        "hour": time.hour,
        "minute": time.minute,
        "second": time.second,
    }


def _encode_domain_graph(graph: DomainGraph) -> object:
    entities = map(_encode_entity, graph.entities)
    relationships = map(_encode_relationship, graph.relationships)
    obj = {"entities": entities, "relationships": relationships}
    if graph.timestamp is None:
        return obj
    else:
        history_timestamp = _encode_date_time(graph.timestamp)
        return {**obj, "historyTimestamp": history_timestamp}


def _encode_entity(entity: Entity) -> object:
    assignments = map(_encode_attribute_assignment, entity.attribute_assignments)
    return {
        "attributeAssignments": assignments,
        "id": entity.id,
        "name": entity.name,
        "type": entity.type,
    }


def _encode_level(level: Level) -> object:
    if level == Level.ALERT:
        return "alert"
    else:
        return "info"


def _encode_relationship(relationship: Relationship) -> object:
    assignments = map(_encode_attribute_assignment, relationship.attribute_assignments)
    return {
        "attributeAssignments": assignments,
        "fromEntityId": relationship.from_entity_id,
        "toEntityId": relationship.to_entity_id,
        "fromEntityType": relationship.from_entity_type,
        "toEntityType": relationship.to_entity_type,
    }


def _encode_time(hour: int, minute: int, second: int) -> object:
    return {"hour": hour, "minute": minute, "second": second}


def _encode_value(value: Value) -> object:
    if isinstance(value, BooleanValue):
        return {"type": "boolean", "value": value.value}

    elif isinstance(value, DateValue):
        date_value = _encode_date(value.year, value.month, value.day)
        return {"type": "date", "value": date_value}

    elif isinstance(value, DateTimeValue):
        date_time_value = _encode_date_time(value.value)
        return {"type": "dateTime", "value": date_time_value}

    elif isinstance(value, NumberValue):
        return {"type": "number", "value": value.value}

    elif isinstance(value, StringValue):
        return {"type": "string", "value": value.value}

    else:
        time_value = _encode_time(value.hour, value.minute, value.second)
        return {"type": "time", "value": time_value}
