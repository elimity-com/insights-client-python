from typing import List

from elimity_insights_client._domain_graph_schema import (
    AttributeType,
    DomainGraphSchema,
)


def attribute_types(entity_type: str, schema: DomainGraphSchema) -> List[AttributeType]:
    return [
        type
        for type in schema.attribute_types
        if not type.archived and type.entity_type == entity_type
    ]


def link_entity_types(entity_type: str, schema: DomainGraphSchema) -> List[str]:
    return [type.id for type in schema.entity_types if type.id != entity_type]
