import logging
from dataclasses import dataclass
from datetime import datetime, time, date, timezone
from enum import Enum
from typing import List, Union

import requests

import http.client as http_client
http_client.HTTPConnection.debuglevel = 2

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

@dataclass
class AttributeAssignment:
    attribute_type_name: str
    value: 'Value'

    def model(self) -> dict:
        return {
            'attributeTypeName': self.attribute_type_name,
            'value': self.value.model()
        }


@dataclass
class AttributeType:
    entity_type: str
    name: str
    type: 'Type'
    description: str

    def model(self) -> dict:
        return {
            'category': self.entity_type,
            'description': self.description,
            'name': self.name,
            'type': self.type.model()
        }


@dataclass
class BooleanValue:
    value: bool

    def model(self) -> dict:
        return {
            'type': Type.BOOLEAN.model(),
            'value': 'true' if self.value else 'false'
        }


class Client:
    def __init__(self, config: 'Config', disable_ssl_check: 'bool') -> None:
        self._config = config
        self._disable_ssl_check = disable_ssl_check
        self._token = ''

    def create_attribute_type(self, attribute_type: AttributeType) -> None:
        body = attribute_type.model()
        path = 'attributeTypes'
        self._post_request(path, body)

    def create_relationship_attribute_type(self, relationship_attribute_type: 'RelationshipAttributeType') -> None:
        body = relationship_attribute_type.model()
        path = 'relationshipAttributeTypes'
        self._post_request(path, body)

    def reload_domain_graph(self, domain_graph: 'DomainGraph') -> None:
        body = domain_graph.model()
        path = 'domain-graph/reload'
        self._post_request(path, body)

    def _post_request(self, path: 'str', body: 'dict') -> None:
        url = '{}/{}'.format(self._config.url, path)
        headers = {'Authorization': 'Bearer {}'.format(self._access_token())}
        resp = requests.post(url,
                             verify=not self._disable_ssl_check,
                             json=body,
                             headers=headers)
        print("response-body: " + resp.text)
        resp.raise_for_status()

    def _access_token(self) -> str:
        if self._token == '':
            self._token = self._get_token()
        return self._token

    def _get_token(self) -> str:
        body = {'type': 'password', 'value': self._config.password}
        url = '{}/authenticate/{}'.format(self._config.url, self._config.username)
        resp = requests.post(url,
                             verify=not self._disable_ssl_check,
                             json=body)
        resp.raise_for_status()
        print("response-body: " + resp.text)
        return resp.json()['token']


@dataclass
class Config:
    password: str
    username: str
    url: str


@dataclass
class DateValue:
    value: date

    def model(self) -> dict:
        return {
            'type': Type.DATE.model(),
            'value': '{:%Y-%m-%d}'.format(self.value)
        }


@dataclass
class DateTimeValue:
    value: datetime

    def model(self) -> dict:
        value = self.value.astimezone(timezone.utc)
        value_str = '{:%Y-%m-%dT%H:%M:%S}Z'.format(value)
        return {
            'type': Type.DATE_TIME.model(),
            'value': value_str
        }


@dataclass
class DomainGraph:
    entities: List['Entity']
    relationships: List['Relationship']

    def model(self) -> dict:
        entities = list(map(Entity.model, self.entities))
        relationships = list(map(Relationship.model, self.relationships))
        return {
            'entities': entities,
            'relationships': relationships
        }


@dataclass
class Entity:
    active: bool
    attribute_assignments: List[AttributeAssignment]
    id: str
    name: str
    type: str

    def model(self) -> dict:
        attribute_assignments = list(map(AttributeAssignment.model, self.attribute_assignments))
        return {
            'active': self.active,
            'attributeAssignments': attribute_assignments,
            'id': self.id,
            'name': self.name,
            'type': self.type
        }


@dataclass
class NumberValue:
    value: float

    def model(self) -> dict:
        return {
            'type': Type.NUMBER.model(),
            'value': '{}'.format(self.value)
        }


@dataclass
class Relationship:
    attribute_assignments: List[AttributeAssignment]
    from_entity_id: str
    from_entity_type: str
    to_entity_id: str
    to_entity_type: str

    def model(self) -> dict:
        attributeAssignments = list(map(AttributeAssignment.model, self.attribute_assignments))
        return {
            'attributeAssignments': attributeAssignments,
            'fromId': self.from_entity_id,
            'toId': self.to_entity_id,
            'fromType': self.from_entity_type,
            'toType': self.to_entity_type
        }


@dataclass
class RelationshipAttributeType:
    from_entity_type: str
    name: str
    to_entity_type: str
    type: 'Type'
    description: str

    def model(self) -> dict:
        return {
            'childType': self.to_entity_type,
            'description': self.description,
            'name': self.name,
            'parentType': self.from_entity_type,
            'type': self.type
        }


@dataclass
class TimeValue:
    value: time

    def model(self) -> dict:
        value_dt = datetime(2000, 1, 1, self.value.hour, self.value.minute, self.value.second,
                            tzinfo=self.value.tzinfo)
        value_dt_utc = value_dt.astimezone(timezone.utc)
        return {
            'type': Type.TIME.model(),
            'value': '{:%H:%M:%S}Z'.format(value_dt_utc)
        }


@dataclass
class StringValue:
    value: str

    def model(self) -> dict:
        return {
            'type': Type.STRING.model(),
            'value': self.value
        }


class Type(Enum):
    BOOLEAN = 1
    DATE = 2
    DATE_TIME = 3
    NUMBER = 4
    STRING = 5
    TIME = 6

    def model(self) -> str:
        if self == Type.BOOLEAN:
            return 'boolean'
        elif self == Type.DATE:
            return 'date'
        elif self == Type.DATE_TIME:
            return 'dateTime'
        elif self == Type.NUMBER:
            return 'number'
        elif self == Type.STRING:
            return 'string'
        elif self == Type.TIME:
            return 'time'


Value = Union[BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue]
