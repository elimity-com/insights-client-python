from dataclasses import dataclass
from datetime import datetime
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
            'value': self.value
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
            'type': self.type
        }


@dataclass
class BooleanValue:
    value: bool


class Client:
    def __init__(self, config: 'Config', disable_ssl_check: 'bool') -> None:
        self.config = config
        self._disable_ssl_check = disable_ssl_check
        self._access_token = self._get_token()

    def create_attribute_type(self, attribute_type: AttributeType) -> None:
        body = attribute_type.model()
        path = 'attributeTypes'
        self._post_request(path, body)

    def create_relationship_attribute_type(self, relationship_attribute_type: 'RelationshipAttributeType') -> None:
        # TODO: implement this when the backend API provides this endpoint
        raise NotImplementedError

    def reload_domain_graph(self, domain_graph: 'DomainGraph') -> None:
        body = domain_graph.model()
        path = 'domain-graph/reload'
        self._post_request(path, body)

    def _get_token(self) -> str:
        body = {'type': 'password', 'value': self.config.password}
        url = '{}/authenticate/{}'.format(self.config.url, self.config.user_name)
        resp = requests.post(url,
                             verify=not self._disable_ssl_check,
                             json=body)
        resp.raise_for_status()
        return resp.json()['token']

    def _post_request(self, path, body) -> None:
        url = '{}/{}'.format(self.config.url, path)
        headers = {'Authorization': 'Bearer {}'.format(self._access_token)}
        resp = requests.post(url,
                             verify=not self._disable_ssl_check,
                             json=body,
                             headers=headers)
        resp.raise_for_status()


@dataclass
class Config:
    password: str
    user_name: str
    url: str


@dataclass
class DateValue:
    value: datetime


@dataclass
class DateTimeValue:
    value: datetime


@dataclass
class DomainGraph:
    entities: List['Entity']
    relationships: List['Relationship']

    def model(self) -> dict:
        entities = list(map(lambda e: e.model(), self.entities))
        relationships = list(map(lambda r: r.model(), self.relationships))
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
        attributeAssignments = list(map(lambda a: a.model(), self.attribute_assignments))
        return {
            'active': self.active,
            'attributeAssignments': attributeAssignments,
            'id': self.id,
            'name': self.name,
            'type': self.type
        }


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

    def model(self) -> dict:
        attributeAssignments = list(map(lambda a: a.model(), self.attribute_assignments))
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


@dataclass
class TimeValue:
    value: datetime


@dataclass
class StringValue:
    value: str


class Type(str, Enum):
    BOOLEAN = 'boolean'
    DATE = 'date'
    DATE_TIME = 'date_time'
    NUMBER = 'number'
    STRING = 'string'
    TIME = 'time'


Value = Union[BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue]
