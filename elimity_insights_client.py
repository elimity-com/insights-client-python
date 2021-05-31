"""
Client for connector interactions with an Elimity Insights server.

Note that this module interprets timestamps without timezone information as
being defined in the local system timezone.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from itertools import chain
from typing import Optional, Union, Any, Iterable, Tuple, Dict, TypeVar, Callable, List
from zlib import compressobj

from dateutil.tz import tzlocal
from dateutil.utils import default_tzinfo
from requests import request, Response
from simplejson import JSONEncoder


@dataclass
class AttributeAssignment:
    """Assignment of a value for an attribute type."""

    attribute_type_id: str
    value: "Value"


@dataclass
class AttributeType:
    """Attribute type for an entity type."""

    archived: bool
    description: str
    entity_type: str
    id: str
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
        json = map(_encode_connector_log, logs)
        json_string = _encoder.encode(json)
        json_bytes = json_string.encode()
        self._post("application/json", json_bytes, "connector-logs")

    def get_domain_graph_schema(self) -> "DomainGraphSchema":
        """Retrieve the domain graph schema."""
        headers = {}
        response = self._request(None, headers, "GET", "domain-graph-schema")
        json = response.json()
        return _decode_domain_graph_schema(json)

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
class DomainGraphSchema:
    """Schema determining valid domain graphs."""

    attribute_types: List[AttributeType]
    entity_types: List["EntityType"]
    relationship_attribute_types: List["RelationshipAttributeType"]


@dataclass
class Entity:
    """Entity of a specific type, including attribute assignments."""

    attribute_assignments: Iterable[AttributeAssignment]
    id: str
    name: str
    type: str


@dataclass
class EntityType:
    """Type of an entity."""

    anonymized: bool
    icon: str
    id: str
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
    id: str
    name: str
    to_entity_type: str
    type: "Type"


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


def _compress_domain_graph(json: Any) -> Iterable[bytes]:
    compress = compressobj()
    for json_string_chunk in _encoder.iterencode(json):
        json_bytes_chunk = json_string_chunk.encode()
        yield compress.compress(json_bytes_chunk)
    yield compress.flush()


def _decode_attribute_type(json: Any) -> AttributeType:
    archived = json["archived"]
    description = json["description"]
    entity_type = json["entityTypeId"]
    id_ = json["id"]
    name = json["name"]
    type_ = json["type"]
    type__ = _decode_type(type_)
    return AttributeType(archived, description, entity_type, id_, name, type__)


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
    id_ = json["id"]
    name = json["name"]
    to_entity_type = json["childType"]
    type_ = json["type"]
    type__ = _decode_type(type_)
    return RelationshipAttributeType(
        archived, description, from_entity_type, id_, name, to_entity_type, type__
    )


def _decode_entity_type(json: Any) -> EntityType:
    anonymized = json["anonymized"]
    icon = json["icon"]
    id = json["id"]
    plural = json["plural"]
    singular = json["singular"]
    return EntityType(anonymized, icon, id, plural, singular)


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


def _encode_attribute_assignment(assignment: AttributeAssignment) -> Any:
    value = _encode_value(assignment.value)
    return {
        "attributeTypeId": assignment.attribute_type_id,
        "value": value,
    }


def _encode_connector_log(log: ConnectorLog) -> Any:
    level = _encode_level(log.level)
    timestamp = _encode_datetime(log.timestamp)
    return {
        "level": level,
        "message": log.message,
        "timestamp": timestamp,
    }


def _encode_date(year: int, month: int, day: int) -> Any:
    return {"year": year, "month": month, "day": day}


def _encode_date_time(time: DateTime) -> Any:
    return {
        "year": time.year,
        "month": time.month,
        "day": time.day,
        "hour": time.hour,
        "minute": time.minute,
        "second": time.second,
    }


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
        history_timestamp = _encode_date_time(graph.timestamp)
        return {**obj, "historyTimestamp": history_timestamp}


def _encode_entity(entity: Entity) -> Any:
    assignments = map(_encode_attribute_assignment, entity.attribute_assignments)
    return {
        "attributeAssignments": assignments,
        "id": entity.id,
        "name": entity.name,
        "type": entity.type,
    }


def _encode_level(level: Level) -> Any:
    if level == Level.ALERT:
        return "alert"
    else:
        return "info"


def _encode_relationship(relationship: Relationship) -> Any:
    assignments = map(_encode_attribute_assignment, relationship.attribute_assignments)
    return {
        "attributeAssignments": assignments,
        "fromEntityId": relationship.from_entity_id,
        "toEntityId": relationship.to_entity_id,
        "fromEntityType": relationship.from_entity_type,
        "toEntityType": relationship.to_entity_type,
    }


def _encode_time(hour: int, minute: int, second: int) -> Any:
    return {"hour": hour, "minute": minute, "second": second}


def _encode_value(value: Value) -> Any:
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


def _map(callable_: Callable[["_T"], "_U"], iterable: Any) -> List["_U"]:
    iterator = map(callable_, iterable)
    return list(iterator)


_encoder = JSONEncoder(iterable_as_array=True)

_T = TypeVar("_T")

_U = TypeVar("_U")
