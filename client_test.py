import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock

from client import Client as ElimityClient, Config, AttributeType, Type, DomainGraph, Entity, Relationship, \
    AttributeAssignment, BooleanValue, DateTimeValue, TimeValue, DateValue, NumberValue, StringValue, \
    RelationshipAttributeType

class TestClient(TestCase):

    def setUp(self) -> None:
        self._patch_post_request = patch('requests.post')
        self._patch_get_token = patch('client.Client._get_token', return_value='token')
        self.post_request_mock = self._patch_post_request.start()
        self.get_token_mock = self._patch_get_token.start()
        self.client_config = Config('password', 'user_name', 'api_url')
        self.elimity_client = ElimityClient(self.client_config, disable_ssl_check=True)
        self.elimity_client._get_token = MagicMock(return_value='token')

    def tearDown(self) -> None:
        self._patch_post_request.stop()
        self._patch_get_token.stop()

    def test_create_attribute_type(self) -> None:
        attribute_type_input = AttributeType(entity_type='foo',
                                             name='bar',
                                             type=Type.string,
                                             description='some description')
        self.elimity_client.create_attribute_type(attribute_type_input)

        expected_url = self.client_config.url + '/attributeTypes'
        expected_json = {
            'category': attribute_type_input.entity_type,
            'description': attribute_type_input.description,
            'name': attribute_type_input.name,
            'type': attribute_type_input.type
        }
        expected_headers = {'Authorization': 'Bearer {}'.format(self.elimity_client._get_token())}
        self.post_request_mock.assert_called_with(expected_url, headers=expected_headers, verify=False,
                                                  json=expected_json)

    def test_create_relationship_attribute_type(self) -> None:
        relationship_attribute_type_input = RelationshipAttributeType(from_entity_type='foo',
                                                                      to_entity_type='bar',
                                                                      name='baz',
                                                                      type=Type.string,
                                                                      description='some description')
        self.elimity_client.create_relationship_attribute_type(relationship_attribute_type_input)

        expected_url = self.client_config.url + '/relationshipAttributeTypes'
        expected_json = {
            'childType': relationship_attribute_type_input.to_entity_type,
            'description': relationship_attribute_type_input.description,
            'name': relationship_attribute_type_input.name,
            'parentType': relationship_attribute_type_input.from_entity_type,
            'type': relationship_attribute_type_input.type
        }
        expected_headers = {'Authorization': 'Bearer {}'.format(self.elimity_client._get_token())}
        self.post_request_mock.assert_called_with(expected_url, headers=expected_headers, verify=False,
                                                  json=expected_json)

    def test_reload_domain_graph(self) -> None:
        graph_input = DomainGraph(
            entities=[Entity(
                active=True,
                attribute_assignments=[
                    AttributeAssignment(
                        attribute_type_name='foo',
                        value=BooleanValue(True)
                    ),
                    AttributeAssignment(
                        attribute_type_name='bar',
                        value=DateValue(datetime.datetime(2006, 1, 2))
                    ),
                    AttributeAssignment(
                        attribute_type_name='baq',
                        value=DateTimeValue(datetime.datetime(2006, 1, 2, 13, 4, 5))
                    ),
                    AttributeAssignment(
                        attribute_type_name='baw',
                        value=NumberValue(99)
                    ),
                    AttributeAssignment(
                        attribute_type_name='bae',
                        value=StringValue('bae string')
                    )
                ],
                id='foo',
                name='bar',
                type='baz'),
                Entity(
                    active=False,
                    attribute_assignments=[
                        AttributeAssignment(
                            attribute_type_name='baz',
                            value=TimeValue(datetime.time(15, 4, 5))
                        )
                    ],
                    id='bar',
                    name='baz',
                    type='foo')
            ],
            relationships=[
                Relationship(
                    attribute_assignments=[],
                    from_entity_id='foo',
                    from_entity_type='baz',
                    to_entity_id='bar',
                    to_entity_type='foo')
            ]
        )
        self.elimity_client.reload_domain_graph(graph_input)

        expected_url = self.client_config.url + '/domain-graph/reload'
        expected_json = {
            'entities': [
                {
                    'active': True,
                    'attributeAssignments': [
                        {
                            'attributeTypeName': 'foo',
                            'value': {
                                'type': 'boolean',
                                'value': 'true'
                            }
                        },
                        {
                            'attributeTypeName': 'bar',
                            'value': {
                                'type': 'date',
                                'value': '2006-01-02'
                            }
                        },
                        {
                            'attributeTypeName': 'baq',
                            'value': {
                                'type': 'date_time',
                                'value': '2006-01-02T12:04:05Z'
                            }
                        },
                        {
                            'attributeTypeName': 'baw',
                            'value': {
                                'type': 'number',
                                'value': '99'
                            }
                        },
                        {
                            'attributeTypeName': 'bae',
                            'value': {
                                'type': 'string',
                                'value': 'bae string'
                            }
                        }
                    ],
                    'id': 'foo',
                    'name': 'bar',
                    'type': 'baz'
                },
                {
                    'active': False,
                    'attributeAssignments': [
                        {
                            'attributeTypeName': 'baz',
                            'value': {
                                'type': 'time',
                                'value': '15:04:05Z'
                            }
                        }
                    ],
                    'id': 'bar',
                    'name': 'baz',
                    'type': 'foo'
                }
            ],
            'relationships': [
                {
                    'attributeAssignments': [],
                    'fromId': 'foo',
                    'fromType': 'baz',
                    'toId': 'bar',
                    'toType': 'foo'
                }
            ]
        }
        expected_headers = {'Authorization': 'Bearer {}'.format(self.elimity_client._get_token())}
        self.post_request_mock.assert_called_with(expected_url, headers=expected_headers, verify=False,
                                                  json=expected_json)
