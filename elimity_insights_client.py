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
from typing import Optional, Union, Any, Iterable, Tuple, Dict, TypeVar, Callable, List
from zlib import compressobj

from dateutil.tz import tzlocal
from dateutil.utils import default_tzinfo
from more_itertools import chunked
from requests import request, Response
from simplejson import JSONEncoder


@dataclass
class AttributeAssignment:
    """Assignment of a value for an attribute type."""

    attribute_type_name: str
    value: "Value"


@dataclass
class AttributeType:
    """Attribute type for an entity type."""

    archived: bool
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

    def create_connector_logs(self, logs: Iterable["ConnectorLog"]) -> None:
        """Create connector logs."""
        body = map(_encode_connector_log, logs)
        self._post(body, "custom-connector-logs")

    def get_domain_graph_schema(self) -> "DomainGraphSchema":
        """Retrieve the domain graph schema."""
        additional_headers = {}
        response = self._request(additional_headers, None, "GET", "domain-graph-schema")
        json = response.json()
        return _decode_domain_graph_schema(json)

    def reload_domain_graph(self, graph: "DomainGraph") -> None:
        """Reload a domain graph."""
        body = _encode_domain_graph(graph)
        self._post(body, "custom-connector-domain-graphs")

    def _post(self, body: Any, path: str) -> None:
        additional_headers = {"Content-Type": "application/prs.deflate-json"}
        data = _encode(body)
        self._request(additional_headers, data, "POST", path)

    def _request(
        self,
        additional_headers: Dict[str, str],
        data: Optional[Iterable[bytes]],
        method: str,
        path: str,
    ) -> Response:
        config = self._config
        url = f"{config.base_path}/{path}"
        cert = _cert(config.certificate)
        authorization = f"Bearer {config.token}"
        headers = {"Authorization": authorization, **additional_headers}
        response = request(
            method, url, cert=cert, data=data, headers=headers, verify=config.verify_ssl
        )
        response.raise_for_status()
        return response


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
class DomainGraphSchema:
    """Schema determining valid domain graphs."""

    attribute_types: List[AttributeType]
    entity_types: List["EntityType"]
    relationship_attribute_types: List["RelationshipAttributeType"]


@dataclass
class Entity:
    """Entity of a specific type, including attribute assignments."""

    active: bool
    attribute_assignments: Iterable[AttributeAssignment]
    id: str
    name: str
    type: str


@dataclass
class EntityType:
    """Type of an entity."""

    icon: str
    key: str
    plural: str
    singular: str


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

    archived: bool
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


Value = Union[
    BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue
]


class Type(Enum):
    """Type of an attribute type, determining valid assignment values."""

    BOOLEAN = auto()
    DATE = auto()
    DATE_TIME = auto()
    NUMBER = auto()
    STRING = auto()
    TIME = auto()


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


def _decode_attribute_type(json: Any) -> AttributeType:
    archived = json["archived"]
    description = json["description"]
    entity_type = json["category"]
    name = json["name"]
    type_ = json["type"]
    type__ = _decode_type(type_)
    return AttributeType(archived, description, entity_type, name, type__)


def _decode_domain_graph_schema(json: Any) -> DomainGraphSchema:
    attribute_types = json["entityAttributeTypes"]
    attribute_types_ = _map(_decode_attribute_type, attribute_types)
    entity_types = json["entityTypes"]
    entity_types_ = _map(_decode_entity_type, entity_types)
    relationship_attribute_types = json["relationshipAttributeTypes"]
    relationship_attribute_types_ = _map(
        _decode_relationship_attribute_types, relationship_attribute_types
    )
    return DomainGraphSchema(
        attribute_types_, entity_types_, relationship_attribute_types_
    )


def _decode_relationship_attribute_types(json: Any) -> RelationshipAttributeType:
    archived = json["archived"]
    description = json.get("description", "")
    from_entity_type = json["parentType"]
    name = json["name"]
    to_entity_type = json["childType"]
    type_ = json["type"]
    type__ = _decode_type(type_)
    return RelationshipAttributeType(
        archived, description, from_entity_type, name, to_entity_type, type__
    )


def _decode_entity_type(json: Any) -> EntityType:
    icon = json["icon"]
    key = json["key"]
    plural = json["plural"]
    singular = json["singular"]
    return EntityType(icon, key, plural, singular)


def _decode_type(json: Any) -> Type:
    if json == "boolean":
        return Type.BOOLEAN
    elif json == "date":
        return Type.DATE
    elif json == "dateTime":
        return Type.DATE_TIME
    elif json == "number":
        return Type.NUMBER
    elif json == "string":
        return Type.STRING
    else:
        return Type.TIME


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


def _encode_time(time_: time) -> Any:
    datetime_ = datetime(
        2000,
        1,
        1,
        time_.hour,
        time_.minute,
        time_.second,
        tzinfo=time_.tzinfo,
    )
    datetime__ = datetime_.astimezone(timezone.utc)
    return f"{datetime__:%H:%M:%S}Z"


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


def _map(callable_: Callable[["_T"], "_U"], iterable: Any) -> List["_U"]:
    iterator = map(callable_, iterable)
    return list(iterator)


_T = TypeVar("_T")

_U = TypeVar("_U")
