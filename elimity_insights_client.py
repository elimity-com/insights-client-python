"""
Client for connector interactions with an Elimity Insights server.

Note that this module interprets timestamps without timezone information as
being defined in the local system timezone.
"""
from dataclasses import dataclass
from datetime import datetime, date, time, timezone
from enum import Enum, auto
from io import DEFAULT_BUFFER_SIZE
from itertools import chain
from typing import Optional, Union, Any, Iterable, Tuple
from zlib import compressobj

from dateutil.tz import tzlocal
from dateutil.utils import default_tzinfo
from more_itertools import chunked
from requests import post
from simplejson import JSONEncoder


@dataclass
class AttributeAssignment:
    """Assignment of a value for an attribute type."""

    attribute_type_name: str
    value: "Value"


@dataclass
class AttributeType:
    """Attribute type for an entity type."""

    description: str
    entity_type: str
    name: str
    type: "Type"


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

    def create_attribute_type(self, type_: AttributeType) -> None:
        """Create a new attribute type."""
        body = _encode_attribute_type(type_)
        self._post(body, "attributeTypes")

    def create_connector_logs(self, logs: Iterable["ConnectorLog"]) -> None:
        """Create connector logs."""
        body = map(_encode_connector_log, logs)
        self._post(body, "connectorLogs")

    def create_relationship_attribute_type(
        self, type_: "RelationshipAttributeType"
    ) -> None:
        """Create a new relationship attribute type."""
        body = _encode_relationship_attribute_type(type_)
        self._post(body, "relationshipAttributeTypes")

    def reload_domain_graph(self, graph: "DomainGraph") -> None:
        """Reload a domain graph."""
        body = _encode_domain_graph(graph)
        self._post(body, "domain-graph/reload")

    def _post(self, body: Any, path: str) -> None:
        data = _encode(body)
        config = self._config
        url = f"{config.base_path}/{path}"
        cert = _cert(config.certificate)
        authorization = f"Bearer {config.token}"
        headers = {
            "Authorization": authorization,
            "Content-Encoding": "deflate",
            "Content-Type": "application/json",
        }
        response = post(
            url, cert=cert, data=data, headers=headers, verify=config.verify_ssl
        )
        response.raise_for_status()


@dataclass
class Config:
    """Configuration for an Elimity Insights client."""

    base_path: str
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
class DateTimeValue:
    """Value to assign for a date-time attribute type."""

    value: datetime


@dataclass
class DateValue:
    """Value to assign for a date attribute type."""

    value: date


@dataclass
class DomainGraph:
    """Snapshot of a complete domain graph at a specific timestamp."""

    entities: Iterable["Entity"]
    relationships: Iterable["Relationship"]
    timestamp: Optional[datetime] = None


@dataclass
class Entity:
    """Entity of a specific type, including attribute assignments."""

    active: bool
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
class RelationshipAttributeType:
    """Attribute type for relationships between entities of specific types."""

    description: str
    from_entity_type: str
    name: str
    to_entity_type: str
    type: "Type"


@dataclass
class StringValue:
    """Value to assign for a string attribute type."""

    value: str


@dataclass
class TimeValue:
    """Value to assign for a time attribute type."""

    value: time


class Type(Enum):
    """Type of an attribute type, determining valid assignment values."""

    BOOLEAN = auto()
    DATE = auto()
    DATE_TIME = auto()
    NUMBER = auto()
    STRING = auto()
    TIME = auto()


Value = Union[
    BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue
]


def _cert(certificate: Certificate) -> Optional[Tuple[str, str]]:
    if certificate is None:
        return None
    else:
        return certificate.certificate_path, certificate.private_key_path


def _compress(chunks: Iterable[bytes]) -> Iterable[bytes]:
    compress = compressobj()
    for chunk in chunks:
        yield compress.compress(chunk)
    yield compress.flush()


def _encode(body: Any) -> Iterable[bytes]:
    encoder = JSONEncoder(iterable_as_array=True)
    chunks = encoder.iterencode(body)
    encoded = map(str.encode, chunks)
    compressed = _compress(encoded)
    chained = chain.from_iterable(compressed)
    buffered = chunked(chained, DEFAULT_BUFFER_SIZE)
    return map(bytes, buffered)


def _encode_attribute_assignment(assignment: AttributeAssignment) -> Any:
    value = _encode_value(assignment.value)
    return {
        "attributeTypeName": assignment.attribute_type_name,
        "value": value,
    }


def _encode_attribute_type(type_: AttributeType) -> Any:
    type__ = _encode_type(type_.type)
    return {
        "category": type_.entity_type,
        "description": type_.description,
        "name": type_.name,
        "type": type__,
    }


def _encode_bool(bool_: bool) -> Any:
    return "true" if bool_ else "false"


def _encode_connector_log(log: ConnectorLog) -> Any:
    level = _encode_level(log.level)
    timestamp = _encode_datetime(log.timestamp)
    return {
        "level": level,
        "message": log.message,
        "timestamp": timestamp,
    }


def _encode_date(date_: date) -> Any:
    return f"{date_:%Y-%m-%d}"


def _encode_datetime(datetime_: datetime) -> Any:
    tzinfo = tzlocal()
    datetime__ = default_tzinfo(datetime_, tzinfo)
    return datetime__.isoformat()


def _encode_domain_graph(graph: DomainGraph) -> Any:
    entities = map(_encode_entity, graph.entities)
    relationships = map(_encode_relationship, graph.relationships)
    obj = {"entities": entities, "relationships": relationships}
    if graph.timestamp is None:
        return obj
    else:
        history_timestamp = _encode_datetime(graph.timestamp)
        return {**obj, "historyTimestamp": history_timestamp}


def _encode_entity(entity: Entity) -> Any:
    assignments = map(_encode_attribute_assignment, entity.attribute_assignments)
    return {
        "active": entity.active,
        "attributeAssignments": assignments,
        "id": entity.id,
        "name": entity.name,
        "type": entity.type,
    }


def _encode_float(float_: float) -> Any:
    return f"{float_}"


def _encode_level(level: Level) -> Any:
    if level == Level.ALERT:
        return "alert"
    else:
        return "info"


def _encode_relationship(relationship: Relationship) -> Any:
    assignments = map(_encode_attribute_assignment, relationship.attribute_assignments)
    return {
        "attributeAssignments": assignments,
        "fromId": relationship.from_entity_id,
        "toId": relationship.to_entity_id,
        "fromType": relationship.from_entity_type,
        "toType": relationship.to_entity_type,
    }


def _encode_relationship_attribute_type(type_: RelationshipAttributeType) -> Any:
    type__ = _encode_type(type_.type)
    return {
        "childType": type_.to_entity_type,
        "description": type_.description,
        "name": type_.name,
        "parentType": type_.from_entity_type,
        "type": type__,
    }


def _encode_time(time_: time) -> Any:
    datetime_ = datetime(
        2000, 1, 1, time_.hour, time_.minute, time_.second, tzinfo=time_.tzinfo,
    )
    datetime__ = datetime_.astimezone(timezone.utc)
    return f"{datetime__:%H:%M:%S}Z"


def _encode_type(type_: Type) -> Any:
    if type_ == Type.BOOLEAN:
        return "boolean"
    elif type_ == Type.DATE:
        return "date"
    elif type_ == Type.DATE_TIME:
        return "dateTime"
    elif type_ == Type.NUMBER:
        return "number"
    elif type_ == Type.STRING:
        return "string"
    else:
        return "time"


def _encode_value(value: Value) -> Any:
    if isinstance(value, BooleanValue):
        boolean_value = _encode_bool(value.value)
        return {"type": "boolean", "value": boolean_value}

    elif isinstance(value, DateValue):
        date_value = _encode_date(value.value)
        return {"type": "date", "value": date_value}

    elif isinstance(value, DateTimeValue):
        date_time_value = _encode_datetime(value.value)
        return {"type": "dateTime", "value": date_time_value}

    elif isinstance(value, NumberValue):
        number_value = _encode_float(value.value)
        return {"type": "number", "value": number_value}

    elif isinstance(value, StringValue):
        return {"type": "string", "value": value.value}

    else:
        time_value = _encode_time(value.value)
        return {"type": "time", "value": time_value}
