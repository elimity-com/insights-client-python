from itertools import starmap
from typing import Dict, Iterable, List

from elimity_insights_client._domain_graph_schema import (
    AttributeType,
    DomainGraphSchema,
)
from elimity_insights_client.api.entities._entity import EntityType


def attribute_types(
    entity_type: EntityType, schemas: Dict[int, DomainGraphSchema]
) -> List[AttributeType]:
    schema = schemas[entity_type.source_id]
    return [
        type
        for type in schema.attribute_types
        if not type.archived and type.entity_type == entity_type.id
    ]


def link_entity_types(
    entity_type: EntityType, schemas: Dict[int, DomainGraphSchema]
) -> List[EntityType]:
    items = schemas.items()
    iters = starmap(_entity_types, items)
    return [typ for iter in iters for typ in iter if typ != entity_type]


def _entity_types(source_id: int, schema: DomainGraphSchema) -> Iterable[EntityType]:
    for type in schema.entity_types:
        yield EntityType(type.id, source_id)
