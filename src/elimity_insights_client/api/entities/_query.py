from typing import Dict, List

from more_itertools import interleave

from elimity_insights_client._domain_graph_schema import (
    AttributeType,
    DomainGraphSchema,
    Type,
)
from elimity_insights_client._util import map_list
from elimity_insights_client.api.entities._entity import EntityType
from elimity_insights_client.api.entities._schema import (
    attribute_types as schema_attribute_types,
)
from elimity_insights_client.api.entities._schema import (
    link_entity_types as schema_link_entity_types,
)
from elimity_insights_client.api.expression import (
    AssignedBooleanExpression,
    AttributeBooleanExpression,
    AttributeDateExpression,
    AttributeDateTimeExpression,
    AttributeNumberExpression,
    AttributeStringExpression,
    AttributeTimeExpression,
    BooleanExpression,
    DateExpression,
    DateTimeExpression,
    LiteralBooleanExpression,
    NumberExpression,
    StringExpression,
    TimeExpression,
)
from elimity_insights_client.api.query import (
    AnyExpression,
    BooleanAnyExpression,
    DateAnyExpression,
    DateTimeAnyExpression,
    DirectLinkGroupByQuery,
    DirectLinkQuery,
    LinkGroupByQuery,
    NumberAnyExpression,
    Ordering,
    Query,
    StringAnyExpression,
    TimeAnyExpression,
)


def query(
    entity_type: EntityType,
    schemas: Dict[int, DomainGraphSchema],
) -> Query:
    def make_link_query(entity_type: EntityType) -> Query:
        link_queries: List[Query] = []
        return _query(entity_type, link_queries, schemas)

    link_entity_types = schema_link_entity_types(entity_type, schemas)
    link_queries = map_list(make_link_query, link_entity_types)
    return _query(entity_type, link_queries, schemas)


def _assigned_inclusion(type: AttributeType) -> AnyExpression:
    expr = AssignedBooleanExpression(type.id, "")
    return BooleanAnyExpression(expr)


def _attribute_inclusion(type: AttributeType) -> AnyExpression:
    id = type.id
    typ = type.type
    if typ is Type.BOOLEAN:
        boolean_expr: BooleanExpression = AttributeBooleanExpression(id, "")
        return BooleanAnyExpression(boolean_expr)
    if typ is Type.DATE:
        date_expr: DateExpression = AttributeDateExpression(id, "")
        return DateAnyExpression(date_expr)
    if typ is Type.DATE_TIME:
        date_time_expr: DateTimeExpression = AttributeDateTimeExpression(id, "")
        return DateTimeAnyExpression(date_time_expr)
    if typ is Type.NUMBER:
        number_expr: NumberExpression = AttributeNumberExpression(id, "")
        return NumberAnyExpression(number_expr)
    if typ is Type.STRING:
        string_expr: StringExpression = AttributeStringExpression(id, "")
        return StringAnyExpression(string_expr)
    time_expr: TimeExpression = AttributeTimeExpression(id, "")
    return TimeAnyExpression(time_expr)


def _inclusions(
    entity_type: EntityType, schemas: Dict[int, DomainGraphSchema]
) -> List[AnyExpression]:
    attribute_types = schema_attribute_types(entity_type, schemas)
    assigned_iter = map(_assigned_inclusion, attribute_types)
    attribute_iter = map(_attribute_inclusion, attribute_types)
    inclusion_iter = interleave(assigned_iter, attribute_iter)
    return list(inclusion_iter)


def _query(
    entity_type: EntityType,
    link_queries: List[Query],
    schemas: Dict[int, DomainGraphSchema],
) -> Query:
    condition = LiteralBooleanExpression(True)
    direct_link_group_by_queries: List[DirectLinkGroupByQuery] = []
    direct_link_queries: List[DirectLinkQuery] = []
    inclusions = _inclusions(entity_type, schemas)
    link_group_by_queries: List[LinkGroupByQuery] = []
    orderings: List[Ordering] = []
    return Query(
        "",
        condition,
        direct_link_group_by_queries,
        direct_link_queries,
        entity_type.id,
        inclusions,
        999999,
        link_group_by_queries,
        link_queries,
        0,
        orderings,
        entity_type.source_id,
    )
