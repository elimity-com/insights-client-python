from datetime import time
from typing import Callable, List, TypeVar

from elimity_insights_client._util import encode_datetime, local_timezone
from elimity_insights_client.api.expression import (
    ActiveBooleanExpression,
    AggregateOperator,
    AllBooleanExpression,
    AnyBooleanExpression,
    AssignedBooleanExpression,
    AttributeBooleanExpression,
    AttributeDateExpression,
    AttributeDateTimeExpression,
    AttributeNumberExpression,
    AttributeStringExpression,
    AttributeTimeExpression,
    BooleanExpression,
    CmpOperator,
    DateCmpBooleanExpression,
    DateExpression,
    DateTimeCmpBooleanExpression,
    DateTimeExpression,
    DirectLinkAggregateNumberExpression,
    DirectlyLinkedToBooleanExpression,
    IdInBooleanExpression,
    IdStringExpression,
    LinkAggregateNumberExpression,
    LinkAssignedBooleanExpression,
    LinkAttributeBooleanExpression,
    LinkAttributeDateExpression,
    LinkAttributeDateTimeExpression,
    LinkAttributeNumberExpression,
    LinkAttributeStringExpression,
    LinkAttributeTimeExpression,
    LinkedToBooleanExpression,
    LiteralBooleanExpression,
    LiteralDateExpression,
    LiteralDateTimeExpression,
    LiteralNumberExpression,
    LiteralStringExpression,
    LiteralTimeExpression,
    MatchBooleanExpression,
    MatchMode,
    MatchOperator,
    NameStringExpression,
    NotBooleanExpression,
    NumberCmpBooleanExpression,
    NumberExpression,
    RelativeDateExpression,
    RelativeDateTimeExpression,
    StringExpression,
    TimeCmpBooleanExpression,
    TimeExpression,
)

_T = TypeVar("_T")
_EncodeFunc = Callable[[_T], object]


def encode_boolean_expression(expression: BooleanExpression) -> object:
    """Encode the given boolean expression to a JSON value."""
    if isinstance(expression, ActiveBooleanExpression):
        return {"reference": expression.reference, "type": "active"}

    if isinstance(expression, AllBooleanExpression):
        return _encode_composite_boolean_expression(expression.exprs, "all")

    if isinstance(expression, AnyBooleanExpression):
        return _encode_composite_boolean_expression(expression.exprs, "any")

    if isinstance(expression, AssignedBooleanExpression):
        return {
            "attributeType": expression.attribute_type,
            "reference": expression.reference,
            "type": "assigned",
        }

    if isinstance(expression, AttributeBooleanExpression):
        return _encode_attribute_expression(
            expression.attribute_type, expression.reference
        )

    if isinstance(expression, DateCmpBooleanExpression):
        return _encode_cmp_expression(
            encode_date_expression,
            expression.lhs,
            expression.operator,
            expression.rhs,
            "dateCmp",
        )

    if isinstance(expression, DateTimeCmpBooleanExpression):
        return _encode_cmp_expression(
            encode_date_time_expression,
            expression.lhs,
            expression.operator,
            expression.rhs,
            "dateTimeCmp",
        )

    if isinstance(expression, DirectlyLinkedToBooleanExpression):
        condition = encode_boolean_expression(expression.condition)
        return {
            "alias": expression.alias,
            "condition": condition,
            "entityType": expression.entity_type,
            "linkAlias": expression.link_alias,
            "sourceId": expression.source_id,
            "type": "directlyLinkedTo",
        }

    if isinstance(expression, IdInBooleanExpression):
        return {
            "ids": expression.ids,
            "reference": expression.reference,
            "type": "idInBooleanExpression",
        }

    if isinstance(expression, LinkedToBooleanExpression):
        condition = encode_boolean_expression(expression.condition)
        return {
            "alias": expression.alias,
            "condition": condition,
            "entityType": expression.entity_type,
            "sourceId": expression.source_id,
            "type": "linkedTo",
        }

    if isinstance(expression, LinkAssignedBooleanExpression):
        return {
            "linkAttributeType": expression.link_attribute_type,
            "linkReference": expression.link_reference,
            "type": "linkAssigned",
        }

    if isinstance(expression, LinkAttributeBooleanExpression):
        return _encode_link_attribute_expression(
            expression.link_attribute_type, expression.link_reference
        )

    if isinstance(expression, LiteralBooleanExpression):
        return {"boolean": expression.boolean, "type": "literal"}

    if isinstance(expression, MatchBooleanExpression):
        lhs = encode_string_expression(expression.lhs)
        mode = _encode_match_mode(expression.mode)
        operator = _encode_match_operator(expression.operator)
        rhs = encode_string_expression(expression.rhs)
        return {
            "lhs": lhs,
            "mode": mode,
            "operator": operator,
            "rhs": rhs,
            "type": "match",
        }

    if isinstance(expression, NotBooleanExpression):
        expr = encode_boolean_expression(expression.expr)
        return {"expr": expr, "type": "not"}

    if isinstance(expression, NumberCmpBooleanExpression):
        return _encode_cmp_expression(
            encode_number_expression,
            expression.lhs,
            expression.operator,
            expression.rhs,
            "numberCmp",
        )

    if isinstance(expression, TimeCmpBooleanExpression):
        return _encode_cmp_expression(
            encode_time_expression,
            expression.lhs,
            expression.operator,
            expression.rhs,
            "timeCmp",
        )


def encode_date_expression(expression: DateExpression) -> object:
    """Encode the given date expression to a JSON value."""
    if isinstance(expression, AttributeDateExpression):
        return _encode_attribute_expression(
            expression.attribute_type, expression.reference
        )

    if isinstance(expression, LinkAttributeDateExpression):
        return _encode_link_attribute_expression(
            expression.link_attribute_type, expression.link_reference
        )

    if isinstance(expression, LiteralDateExpression):
        date = expression.date.isoformat()
        return {"date": date, "type": "literal"}

    if isinstance(expression, RelativeDateExpression):
        return {
            "days": expression.days,
            "future": expression.future,
            "months": expression.months,
            "type": "relativeDate",
            "years": expression.years,
        }


def encode_date_time_expression(expression: DateTimeExpression) -> object:
    """Encode the given date-time expression to a JSON value."""
    if isinstance(expression, AttributeDateTimeExpression):
        return _encode_attribute_expression(
            expression.attribute_type, expression.reference
        )

    if isinstance(expression, LinkAttributeDateTimeExpression):
        return _encode_link_attribute_expression(
            expression.link_attribute_type, expression.link_reference
        )

    if isinstance(expression, LiteralDateTimeExpression):
        date_time = encode_datetime(expression.date_time)
        return {"dateTime": date_time, "type": "literal"}

    if isinstance(expression, RelativeDateTimeExpression):
        return {
            "days": expression.days,
            "future": expression.future,
            "hours": expression.hours,
            "minutes": expression.minutes,
            "months": expression.months,
            "seconds": expression.seconds,
            "type": "relativeDateTime",
            "years": expression.years,
        }


def encode_number_expression(expression: NumberExpression) -> object:
    """Encode the given number expression to a JSON value."""
    if isinstance(expression, AttributeNumberExpression):
        return _encode_attribute_expression(
            expression.attribute_type, expression.reference
        )

    if isinstance(expression, DirectLinkAggregateNumberExpression):
        condition = encode_boolean_expression(expression.condition)
        expr = encode_number_expression(expression.expr)
        op = _encode_aggregate_operator(expression.op)
        return {
            "alias": expression.alias,
            "condition": condition,
            "entityType": expression.entity_type,
            "linkAlias": expression.link_alias,
            "expr": expr,
            "op": op,
            "sourceId": expression.source_id,
            "type": "directLinkAggregate",
        }

    if isinstance(expression, LinkAggregateNumberExpression):
        condition = encode_boolean_expression(expression.condition)
        expr = encode_number_expression(expression.expr)
        op = _encode_aggregate_operator(expression.op)
        return {
            "alias": expression.alias,
            "condition": condition,
            "entityType": expression.entity_type,
            "expr": expr,
            "op": op,
            "sourceId": expression.source_id,
            "type": "linkAggregate",
        }

    if isinstance(expression, LinkAttributeNumberExpression):
        return _encode_link_attribute_expression(
            expression.link_attribute_type, expression.link_reference
        )

    if isinstance(expression, LiteralNumberExpression):
        return {"number": expression.number, "type": "literal"}


def encode_string_expression(expression: StringExpression) -> object:
    """Encode the given string expression to a JSON value."""
    if isinstance(expression, AttributeStringExpression):
        return _encode_attribute_expression(
            expression.attribute_type, expression.reference
        )

    if isinstance(expression, IdStringExpression):
        return {"reference": expression.reference, "type": "id"}

    if isinstance(expression, LinkAttributeStringExpression):
        return _encode_link_attribute_expression(
            expression.link_attribute_type, expression.link_reference
        )

    if isinstance(expression, LiteralStringExpression):
        return {"string": expression.string, "type": "literal"}

    if isinstance(expression, NameStringExpression):
        return {"reference": expression.reference, "type": "name"}


def encode_time_expression(expression: TimeExpression) -> object:
    """Encode the given time expression to a JSON value."""
    if isinstance(expression, AttributeTimeExpression):
        return _encode_attribute_expression(
            expression.attribute_type, expression.reference
        )

    if isinstance(expression, LinkAttributeTimeExpression):
        return _encode_link_attribute_expression(
            expression.link_attribute_type, expression.link_reference
        )

    if isinstance(expression, LiteralTimeExpression):
        time = _set_timezone(expression.time).isoformat()
        return {"time": time, "type": "literal"}


def _encode_aggregate_operator(operator: AggregateOperator) -> object:
    if operator is AggregateOperator.AVG:
        return "avg"

    if operator is AggregateOperator.COUNT:
        return "count"

    if operator is AggregateOperator.MAX:
        return "max"

    if operator is AggregateOperator.MIN:
        return "min"

    if operator is AggregateOperator.SUM:
        return "sum"


def _encode_attribute_expression(attribute_type: str, reference: str) -> object:
    return {
        "attributeType": attribute_type,
        "reference": reference,
        "type": "attribute",
    }


def _encode_cmp_operator(operator: CmpOperator) -> object:
    if operator is CmpOperator.EQ:
        return "eq"

    if operator is CmpOperator.GT:
        return "gt"

    if operator is CmpOperator.GTE:
        return "gte"

    if operator is CmpOperator.LT:
        return "lt"

    if operator is CmpOperator.LTE:
        return "lte"

    if operator is CmpOperator.NEQ:
        return "neq"


def _encode_composite_boolean_expression(
    exprs: List[BooleanExpression], type: str
) -> object:
    expr_iter = map(encode_boolean_expression, exprs)
    return {"exprs": expr_iter, "type": type}


def _encode_cmp_expression(
    func: _EncodeFunc[_T], lhs: _T, operator: CmpOperator, rhs: _T, type: str
) -> object:
    lhs_obj = func(lhs)
    operator_obj = _encode_cmp_operator(operator)
    rhs_obj = func(rhs)
    return {
        "lhs": lhs_obj,
        "operator": operator_obj,
        "rhs": rhs_obj,
        "type": type,
    }


def _encode_link_attribute_expression(
    link_attribute_type: str, link_reference: str
) -> object:
    return {
        "linkAttributeType": link_attribute_type,
        "linkReference": link_reference,
        "type": "linkAttribute",
    }


def _encode_match_mode(mode: MatchMode) -> object:
    if mode is MatchMode.CASE_INSENSITIVE:
        return "caseInsensitive"

    if mode is MatchMode.CASE_SENSITIVE:
        return "caseSensitive"


def _encode_match_operator(operator: MatchOperator) -> object:
    if operator is MatchOperator.CONTAINS:
        return "contains"

    if operator is MatchOperator.ENDS_WITH:
        return "endsWith"

    if operator is MatchOperator.EQUALS:
        return "equals"

    if operator is MatchOperator.STARTS_WITH:
        return "startsWith"


def _set_timezone(time: time) -> time:
    if time.tzinfo is None:
        return time.replace(tzinfo=local_timezone)
    return time
