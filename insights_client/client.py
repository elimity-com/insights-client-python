import http.client as http_client
import logging
from dataclasses import dataclass
from datetime import datetime, time, date, timezone
from enum import Enum, auto
from io import DEFAULT_BUFFER_SIZE
from json import JSONEncoder
from typing import List, Union, Iterable, Any

import requests
import urllib3


class _DomainGraphEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, AttributeAssignment):
            return {"attributeTypeName": o.attribute_type_name, "value": o.value}
        elif isinstance(o, BooleanValue):
            return {"type": "boolean", "value": "true" if o.value else "false"}
        elif isinstance(o, DateValue):
            value = "{:%Y-%m-%d}".format(o.value)
            return {"type": "date", "value": value}
        elif isinstance(o, DateTimeValue):
            value = _marshal_datetime(o.value)
            return {"type": "dateTime", "value": value}
        elif isinstance(o, DomainGraph):
            return {"entities": o.entities, "relationships": o.relationships}
        elif isinstance(o, Entity):
            return {
                "active": o.active,
                "attributeAssignments": o.attribute_assignments,
                "id": o.id,
                "name": o.name,
                "type": o.type,
            }
        elif isinstance(o, NumberValue):
            value = "{}".format(o.value)
            return {"type": "number", "value": value}
        elif isinstance(o, Relationship):
            return {
                "attributeAssignments": o.attribute_assignments,
                "fromId": o.from_entity_id,
                "toId": o.to_entity_id,
                "fromType": o.from_entity_type,
                "toType": o.to_entity_type,
            }
        elif isinstance(o, StringValue):
            return {"type": "string", "value": o.value}
        elif isinstance(o, TimeValue):
            dt_value = datetime(
                2000,
                1,
                1,
                o.value.hour,
                o.value.minute,
                o.value.second,
                tzinfo=o.value.tzinfo,
            )
            utc_dt_value = dt_value.astimezone(timezone.utc)
            value = "{:%H:%M:%S}Z".format(utc_dt_value)
            return {"type": "time", "value": value}
        else:
            return JSONEncoder.default(self, o)


@dataclass
class AttributeAssignment:
    attribute_type_name: str
    value: "Value"


@dataclass
class AttributeType:
    entity_type: str
    name: str
    type: "Type"
    description: str

    def model(self) -> dict:
        return {
            "category": self.entity_type,
            "description": self.description,
            "name": self.name,
            "type": self.type.model(),
        }


@dataclass
class BooleanValue:
    value: bool


class Client:
    def __init__(self, config: "Config", disable_ssl_check: "bool") -> None:
        self._config = config
        self._disable_ssl_check = disable_ssl_check
        self._token = config.token

        if config.debug:
            _enable_debug_logging()

        if disable_ssl_check:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def create_attribute_type(self, attribute_type: AttributeType) -> None:
        body = attribute_type.model()
        path = "attributeTypes"
        self._post_request(path, body)

    def create_connector_logs(self, logs: List["ConnectorLog"]) -> None:
        model_iter = map(_marshal_connector_log, logs)
        models = list(model_iter)
        self._post_request("connectorLogs", models)

    def create_relationship_attribute_type(
        self, relationship_attribute_type: "RelationshipAttributeType"
    ) -> None:
        body = relationship_attribute_type.model()
        path = "relationshipAttributeTypes"
        self._post_request(path, body)

    @property
    def _debug(self) -> bool:
        return self._config.debug

    def reload_domain_graph(self, domain_graph: "DomainGraph") -> None:
        path = "domain-graph/reload"
        body = _stream_domain_graph(domain_graph)
        self._post_request(path, body, stream=True)

    def _post_request(self, path: "str", body, stream=False) -> None:
        url = "{}/{}".format(self._config.url, path)
        authorization = "Bearer {}".format(self._token)
        headers = {"Authorization": authorization, "Content-Type": "application/json"}
        kwargs = {"data": body} if stream else {"json": body}
        resp = requests.post(
            url, verify=not self._disable_ssl_check, headers=headers, **kwargs
        )

        if self._debug:
            print("response-body: " + resp.text)
        resp.raise_for_status()


def _enable_debug_logging():
    http_client.HTTPConnection.debuglevel = 2

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


@dataclass
class Config:
    token: str
    url: str
    debug: bool


@dataclass
class ConnectorLog:
    level: "Level"
    message: str
    timestamp: datetime


@dataclass
class DateValue:
    value: date


@dataclass
class DateTimeValue:
    value: datetime


@dataclass
class DomainGraph:
    entities: List["Entity"]
    relationships: List["Relationship"]


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
    from_entity_type: str
    name: str
    to_entity_type: str
    type: "Type"
    description: str

    def model(self) -> dict:
        return {
            "childType": self.to_entity_type,
            "description": self.description,
            "name": self.name,
            "parentType": self.from_entity_type,
            "type": self.type,
        }


@dataclass
class TimeValue:
    value: time


@dataclass
class StringValue:
    value: str


class Type(Enum):
    BOOLEAN = auto()
    DATE = auto()
    DATE_TIME = auto()
    NUMBER = auto()
    STRING = auto()
    TIME = auto()

    def model(self) -> str:
        if self == Type.BOOLEAN:
            return "boolean"
        elif self == Type.DATE:
            return "date"
        elif self == Type.DATE_TIME:
            return "dateTime"
        elif self == Type.NUMBER:
            return "number"
        elif self == Type.STRING:
            return "string"
        elif self == Type.TIME:
            return "time"


Value = Union[
    BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue
]


def _marshal_connector_log(log: ConnectorLog) -> Any:
    level = _marshal_level(log.level)
    timestamp = _marshal_datetime(log.timestamp)
    return {
        "level": level,
        "message": log.message,
        "timestamp": timestamp,
    }


def _marshal_datetime(time: datetime) -> Any:
    # FIXME does not work on Windows, see https://bugs.python.org/issue36759
    t = time.astimezone(timezone.utc)
    return "{:%Y-%m-%dT%H:%M:%S}Z".format(t)


def _marshal_level(level: Level) -> Any:
    if level == Level.ALERT:
        return "alert"
    elif level == Level.INFO:
        return "info"
    else:
        raise ValueError("unreachable")


def _stream_domain_graph(domain_graph: DomainGraph) -> Iterable[bytes]:
    encoder = _DomainGraphEncoder()
    buffer = bytearray()

    for chunk in encoder.iterencode(domain_graph):
        chunk_bytes = chunk.encode()
        buffer.extend(chunk_bytes)

        if len(buffer) > DEFAULT_BUFFER_SIZE:
            yield bytes(buffer)
            buffer.clear()

    yield bytes(buffer)
