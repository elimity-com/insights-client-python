from dataclasses import dataclass
from typing import Dict, List

from more_itertools import chunked

from elimity_insights_client._domain_graph_schema import (
    AttributeType,
    DomainGraphSchema,
)
from elimity_insights_client._util import map_list
from elimity_insights_client.api.entities._entity import Entity, EntityType, Link
from elimity_insights_client.api.entities._schema import (
    attribute_types as schema_attribute_types,
)
from elimity_insights_client.api.entities._schema import (
    link_entity_types as schema_link_entity_types,
)
from elimity_insights_client.api.query_results_page import (
    BooleanValue,
    QueryResult,
    QueryResultsPage,
    Value,
)


@dataclass
class _AttributeAssignment:
    assigned: bool
    attribute_type: str
    value: Value


@dataclass
class _LinkGroup:
    entity_type: EntityType
    links: List[Link]


def parse_query_results_page(
    entity_type: EntityType,
    page: QueryResultsPage,
    schemas: Dict[int, DomainGraphSchema],
) -> List[Entity]:
    def make_entity(result: QueryResult) -> Entity:
        entity = _link(entity_type, result, schemas)

        def make_group(entity_type: EntityType, page: QueryResultsPage) -> _LinkGroup:
            def make_link(result: QueryResult) -> Link:
                return _link(entity_type, result, schemas)

            links = map_list(make_link, page.results)
            return _LinkGroup(entity_type, links)

        link_entity_types = schema_link_entity_types(entity_type, schemas)
        group_iter = map(make_group, link_entity_types, result.link_pages)
        links = {group.entity_type: group.links for group in group_iter}
        return Entity(entity.attribute_assignments, entity.id, links, entity.name)

    return map_list(make_entity, page.results)


def _attribute_assignment(
    inclusions: List[Value], type: AttributeType
) -> _AttributeAssignment:
    assigned_inclusion, value_inclusion = inclusions
    assigned = assigned_inclusion == BooleanValue(True)
    return _AttributeAssignment(assigned, type.id, value_inclusion)


def _link(
    entity_type: EntityType, result: QueryResult, schemas: Dict[int, DomainGraphSchema]
) -> Link:
    inclusions_iter = chunked(result.inclusions, 2)
    attribute_types = schema_attribute_types(entity_type, schemas)
    assignment_iter = map(_attribute_assignment, inclusions_iter, attribute_types)
    assignments = {
        assignment.attribute_type: assignment.value
        for assignment in assignment_iter
        if assignment.assigned
    }
    entity = result.entity
    return Link(assignments, entity.id, entity.name)
