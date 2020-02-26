from dataclasses import dataclass
from datetime import datetime, time, date, timezone
from enum import Enum
from typing import List, Union

import requests


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
            'type': Type.boolean.model(),
            'value': 'true' if self.value else 'false'
        }


class Client:
    def __init__(self, config: 'Config', disable_ssl_check: 'bool') -> None:
        self._config = config
        self._disable_ssl_check = disable_ssl_check
        self._access_token = self._get_token(config.password, config.user_name, config.url, disable_ssl_check)

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
        headers = {'Authorization': 'Bearer {}'.format(self._access_token)}
        resp = requests.post(url,
                             verify=not self._disable_ssl_check,
                             json=body,
                             headers=headers)
        resp.raise_for_status()

    @staticmethod
    def _get_token(password: 'str', user_name: 'str', url: 'str', disable_ssl_check: 'bool') -> str:
        body = {'type': 'password', 'value': password}
        url = '{}/authenticate/{}'.format(url, user_name)
        resp = requests.post(url,
                             verify=not disable_ssl_check,
                             json=body)
        resp.raise_for_status()
        return resp.json()['token']


@dataclass
class Config:
    password: str
    user_name: str
    url: str


@dataclass
class DateValue:
    value: date

    def model(self) -> dict:
        return {
            'type': Type.date.model(),
            'value': '{:%Y-%m-%d}'.format(self.value)
        }


@dataclass
class DateTimeValue:
    value: datetime

    def model(self) -> dict:
        value = self.value.astimezone(timezone.utc)
        value_str = '{:%Y-%m-%dT%H:%M:%S}Z'.format(value)
        return {
            'type': Type.date_time.model(),
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
            'type': Type.number.model(),
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
            'type': Type.time.model(),
            'value': '{:%H:%M:%S}Z'.format(value_dt_utc)
        }


@dataclass
class StringValue:
    value: str

    def model(self) -> dict:
        return {
            'type': Type.string.model(),
            'value': self.value
        }


class Type(Enum):
    boolean = 1
    date = 2
    date_time = 3
    number = 4
    string = 5
    time = 6

    def model(self) -> str:
        if self == Type.boolean:
            return 'boolean'
        elif self == Type.date:
            return 'date'
        elif self ==  Type.date_time:
            return 'dateTime'
        elif self == Type.number:
            return 'number'
        elif self == Type.string:
            return 'string'
        elif self == Type.time:
            return 'time'


Value = Union[BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue]
