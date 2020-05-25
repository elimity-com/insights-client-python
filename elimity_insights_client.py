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
from json import JSONEncoder
from typing import List, Optional, Union, Any, Iterable
from zlib import compressobj

from dateutil.tz import tzlocal
from dateutil.utils import default_tzinfo
from more_itertools import ichunked
from requests import post


@dataclass
class AttributeAssignment:
    attribute_type_name: str
    value: "Value"


@dataclass
class AttributeType:
    description: str
    entity_type: str
    name: str
    type: "Type"


@dataclass
class BooleanValue:
    value: bool


class Client:
    def __init__(self, config: "Config") -> None:
        self._config = config

    def create_attribute_type(self, type_: AttributeType) -> None:
        body = _encode_attribute_type(type_)
        self._post(body, "attributeTypes")

    def create_connector_logs(self, logs: List["ConnectorLog"]) -> None:
        body = map(_encode_connector_log, logs)
        body_ = list(body)
        self._post(body_, "connectorLogs")

    def create_relationship_attribute_type(
        self, type_: "RelationshipAttributeType"
    ) -> None:
        body = _encode_relationship_attribute_type(type_)
        self._post(body, "relationshipAttributeTypes")

    def reload_domain_graph(self, graph: "DomainGraph") -> None:
        body = _encode_domain_graph(graph)
        self._post(body, "domain-graph/reload")

    def _post(self, body: Any, path: str) -> None:
        url = f"{self._config.base_path}/{path}"
        authorization = f"Bearer {self._config.token}"
        headers = {
            "Authorization": authorization,
            "Content-Encoding": "deflate",
            "Content-Type": "application/json",
        }
        data = _encode(body)
        response = post(url, headers=headers, data=data)
        response.raise_for_status()


@dataclass
class Config:
    base_path: str
    token: str
    verify_ssl: bool = True


@dataclass
class ConnectorLog:
    level: "Level"
    message: str
    timestamp: datetime


@dataclass
class DateTimeValue:
    value: datetime


@dataclass
class DateValue:
    value: date


@dataclass
class DomainGraph:
    entities: List["Entity"]
    relationships: List["Relationship"]
    timestamp: Optional[datetime] = None


@dataclass
class Entity:
    active: bool
    attribute_assignments: List[AttributeAssignment]
    id: str
    name: str
    type: str


class Level(Enum):
    ALERT = auto()
    INFO = auto()


@dataclass
class NumberValue:
    value: float


@dataclass
class Relationship:
    attribute_assignments: List[AttributeAssignment]
    from_entity_id: str
    from_entity_type: str
    to_entity_id: str
    to_entity_type: str


@dataclass
class RelationshipAttributeType:
    description: str
    from_entity_type: str
    name: str
    to_entity_type: str
    type: "Type"


@dataclass
class StringValue:
    value: str


@dataclass
class TimeValue:
    value: time


class Type(Enum):
    BOOLEAN = auto()
    DATE = auto()
    DATE_TIME = auto()
    NUMBER = auto()
    STRING = auto()
    TIME = auto()


Value = Union[
    BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue
]


def _compress(chunks: Iterable[bytes]) -> Iterable[bytes]:
    compress = compressobj()
    for chunk in chunks:
        yield compress.compress(chunk)
    yield compress.flush()


def _encode(body: Any) -> Iterable[bytes]:
    encoder = JSONEncoder()
    chunks = encoder.iterencode(body)
    encoded = map(str.encode, chunks)
    compressed = _compress(encoded)
    chained = chain.from_iterable(compressed)
    buffered = ichunked(chained, DEFAULT_BUFFER_SIZE)
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
    entities_ = list(entities)
    relationships = map(_encode_relationship, graph.relationships)
    relationships_ = list(relationships)
    obj = {"entities": entities_, "relationships": relationships_}
    if graph.timestamp is None:
        return obj
    else:
        history_timestamp = _encode_datetime(graph.timestamp)
        return {**obj, "historyTimestamp": history_timestamp}


def _encode_entity(entity: Entity) -> Any:
    assignments = map(_encode_attribute_assignment, entity.attribute_assignments)
    assignments_ = list(assignments)
    return {
        "active": entity.active,
        "attributeAssignments": assignments_,
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
    assignments_ = list(assignments)
    return {
        "attributeAssignments": assignments_,
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
