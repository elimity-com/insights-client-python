from elimity_insights_client.api._encode_expression import (
    encode_boolean_expression,
    encode_date_expression,
    encode_date_time_expression,
    encode_number_expression,
    encode_string_expression,
    encode_time_expression,
)
from elimity_insights_client.api.query import (
    AnyExpression,
    BooleanAnyExpression,
    DateAnyExpression,
    DateTimeAnyExpression,
    DirectedGroupOrdering,
    Direction,
    DirectLinkGroupByQuery,
    DirectLinkQuery,
    Grouping,
    GroupOrdering,
    GroupOrderingType,
    LinkGroupByQuery,
    NumberAnyExpression,
    Ordering,
    Query,
    StringAnyExpression,
    TimeAnyExpression,
    UnspecifiedGroupOrdering,
)


def encode_query(query: Query) -> object:
    condition = encode_boolean_expression(query.condition)
    direct_link_group_by_queries = map(
        _encode_direct_link_group_by_query, query.direct_link_group_by_queries
    )
    direct_link_queries = map(_encode_direct_link_query, query.direct_link_queries)
    include = map(_encode_any_expression, query.include)
    link_group_by_queries = map(
        _encode_link_group_by_query, query.link_group_by_queries
    )
    link_queries = map(encode_query, query.link_queries)
    order_by = map(_encode_ordering, query.order_by)
    return {
        "alias": query.alias,
        "condition": condition,
        "directLinkGroupByQueries": direct_link_group_by_queries,
        "directLinkQueries": direct_link_queries,
        "entityType": query.entity_type,
        "include": include,
        "limit": query.limit,
        "linkGroupByQueries": link_group_by_queries,
        "linkQueries": link_queries,
        "offset": query.offset,
        "orderBy": order_by,
        "sourceId": query.source_id,
    }


def _encode_any_expression(expression: AnyExpression) -> object:
    if isinstance(expression, BooleanAnyExpression):
        expr = encode_boolean_expression(expression.expr)
        return {"expr": expr, "type": "boolean"}

    if isinstance(expression, DateAnyExpression):
        expr = encode_date_expression(expression.expr)
        return {"expr": expr, "type": "date"}

    if isinstance(expression, DateTimeAnyExpression):
        expr = encode_date_time_expression(expression.expr)
        return {"expr": expr, "type": "dateTime"}

    if isinstance(expression, NumberAnyExpression):
        expr = encode_number_expression(expression.expr)
        return {"expr": expr, "type": "number"}

    if isinstance(expression, StringAnyExpression):
        expr = encode_string_expression(expression.expr)
        return {"expr": expr, "type": "string"}

    if isinstance(expression, TimeAnyExpression):
        expr = encode_time_expression(expression.expr)
        return {"expr": expr, "type": "time"}


def _encode_direction(direction: Direction) -> object:
    if direction is Direction.ASC:
        return "asc"

    if direction is Direction.DESC:
        return "desc"


def _encode_direct_link_group_by_query(query: DirectLinkGroupByQuery) -> object:
    condition = encode_boolean_expression(query.condition)
    group_by = map(_encode_grouping, query.group_by)
    return {
        "alias": query.alias,
        "condition": condition,
        "entityType": query.entity_type,
        "groupBy": group_by,
        "linkAlias": query.link_alias,
        "sourceId": query.source_id,
    }


def _encode_direct_link_query(query: DirectLinkQuery) -> object:
    condition = encode_boolean_expression(query.condition)
    direct_link_group_by_queries = map(
        _encode_direct_link_group_by_query, query.direct_link_group_by_queries
    )
    direct_link_queries = map(_encode_direct_link_query, query.direct_link_queries)
    include = map(_encode_any_expression, query.include)
    link_group_by_queries = map(
        _encode_link_group_by_query, query.link_group_by_queries
    )
    link_queries = map(encode_query, query.link_queries)
    order_by = map(_encode_ordering, query.order_by)
    return {
        "alias": query.alias,
        "condition": condition,
        "directLinkGroupByQueries": direct_link_group_by_queries,
        "directLinkQueries": direct_link_queries,
        "entityType": query.entity_type,
        "include": include,
        "limit": query.limit,
        "linkAlias": query.link_alias,
        "linkGroupByQueries": link_group_by_queries,
        "linkQueries": link_queries,
        "offset": query.offset,
        "orderBy": order_by,
        "sourceId": query.source_id,
    }


def _encode_grouping(grouping: Grouping) -> object:
    key = _encode_any_expression(grouping.key)
    ordering = _encode_group_ordering(grouping.ordering)
    return {"key": key, "ordering": ordering}


def _encode_group_ordering(ordering: GroupOrdering) -> object:
    if isinstance(ordering, DirectedGroupOrdering):
        direction = _encode_direction(ordering.direction)
        type = _encode_group_ordering_type(ordering.type)
        return {"direction": direction, "type": type}

    if isinstance(ordering, UnspecifiedGroupOrdering):
        return {"type": "none"}


def _encode_group_ordering_type(type: GroupOrderingType) -> object:
    if type is GroupOrderingType.COUNT:
        return "count"

    if type is GroupOrderingType.LABEL:
        return "label"


def _encode_link_group_by_query(query: LinkGroupByQuery) -> object:
    condition = encode_boolean_expression(query.condition)
    group_by = map(_encode_grouping, query.group_by)
    return {
        "alias": query.alias,
        "condition": condition,
        "entityType": query.entity_type,
        "groupBy": group_by,
        "sourceId": query.source_id,
    }


def _encode_ordering(ordering: Ordering) -> object:
    any_expression = _encode_any_expression(ordering.any_expression)
    direction = _encode_direction(ordering.direction)
    return {
        "anyExpression": any_expression,
        "direction": direction,
    }
