from typing import List

from typing_extensions import NotRequired, TypedDict

from elimity_insights_client._domain_graph_schema import (
    AttributeType,
    DomainGraphSchema,
    EntityType,
    RelationshipAttributeType,
    Type,
)
from elimity_insights_client._util import map_list

AttributeTypeDict = TypedDict(
    "AttributeTypeDict",
    {
        "archived": bool,
        "description": str,
        "entityTypeId": str,
        "id": str,
        "name": str,
        "type": str,
    },
)
EntityTypeDict = TypedDict(
    "EntityTypeDict",
    {
        "anonymized": bool,
        "icon": str,
        "id": str,
        "plural": str,
        "singular": str,
    },
)
RelationshipAttributeTypeDict = TypedDict(
    "RelationshipAttributeTypeDict",
    {
        "archived": bool,
        "childType": str,
        "description": NotRequired[str],
        "id": str,
        "name": str,
        "parentType": str,
        "type": str,
    },
)
DomainGraphSchemaDict = TypedDict(
    "DomainGraphSchemaDict",
    {
        "entityAttributeTypes": List[AttributeTypeDict],
        "entityTypes": List[EntityTypeDict],
        "relationshipAttributeTypes": List[RelationshipAttributeTypeDict],
    },
)


def decode_domain_graph_schema(json: DomainGraphSchemaDict) -> DomainGraphSchema:
    """Decode the given JSON value to a domain graph schema."""
    attribute_types = json["entityAttributeTypes"]
    attribute_types_ = map_list(_decode_attribute_type, attribute_types)
    entity_types = json["entityTypes"]
    entity_types_ = map_list(_decode_entity_type, entity_types)
    relationship_attribute_types = json["relationshipAttributeTypes"]
    relationship_attribute_types_ = map_list(
        _decode_relationship_attribute_types, relationship_attribute_types
    )
    return DomainGraphSchema(
        attribute_types_, entity_types_, relationship_attribute_types_
    )


def _decode_attribute_type(json: AttributeTypeDict) -> AttributeType:
    archived = json["archived"]
    description = json["description"]
    entity_type = json["entityTypeId"]
    id_ = json["id"]
    name = json["name"]
    type_ = json["type"]
    type__ = _decode_type(type_)
    return AttributeType(archived, description, entity_type, id_, name, type__)


def _decode_entity_type(json: EntityTypeDict) -> EntityType:
    anonymized = json["anonymized"]
    icon = json["icon"]
    id = json["id"]
    plural = json["plural"]
    singular = json["singular"]
    return EntityType(anonymized, icon, id, plural, singular)


def _decode_relationship_attribute_types(
    json: RelationshipAttributeTypeDict,
) -> RelationshipAttributeType:
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


def _decode_type(json: str) -> Type:
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
