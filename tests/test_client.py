from unittest import TestCase
from unittest.mock import patch

from insights_client.client import (
    Client as ElimityClient,
    Config,
    AttributeType,
    Type,
    RelationshipAttributeType,
)


class TestClient(TestCase):
    def setUp(self) -> None:
        self._patch_post_request = patch("requests.post")
        self.post_request_mock = self._patch_post_request.start()
        self.client_config = Config("token", "api_url", False)
        self.elimity_client = ElimityClient(self.client_config, disable_ssl_check=True)

    def tearDown(self) -> None:
        self._patch_post_request.stop()

    def test_create_attribute_type(self) -> None:
        attribute_type_input = AttributeType(
            entity_type="foo",
            name="bar",
            type=Type.STRING,
            description="some description",
        )
        self.elimity_client.create_attribute_type(attribute_type_input)

        expected_url = self.client_config.url + "/attributeTypes"
        expected_json = {
            "category": "foo",
            "description": "some description",
            "name": "bar",
            "type": "string",
        }
        expected_headers = {
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
        }
        self.post_request_mock.assert_called_with(
            expected_url, headers=expected_headers, verify=False, json=expected_json
        )

    def test_create_relationship_attribute_type(self) -> None:
        relationship_attribute_type_input = RelationshipAttributeType(
            from_entity_type="foo",
            to_entity_type="bar",
            name="baz",
            type=Type.STRING,
            description="some description",
        )
        self.elimity_client.create_relationship_attribute_type(
            relationship_attribute_type_input
        )

        expected_url = self.client_config.url + "/relationshipAttributeTypes"
        expected_json = {
            "childType": relationship_attribute_type_input.to_entity_type,
            "description": relationship_attribute_type_input.description,
            "name": relationship_attribute_type_input.name,
            "parentType": relationship_attribute_type_input.from_entity_type,
            "type": relationship_attribute_type_input.type,
        }
        expected_headers = {
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
        }
        self.post_request_mock.assert_called_with(
            expected_url, headers=expected_headers, verify=False, json=expected_json
        )
