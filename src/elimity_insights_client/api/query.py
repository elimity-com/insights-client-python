"""Type definitions for queries."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Union

from elimity_insights_client.api.expression import (
    BooleanExpression,
    DateExpression,
    DateTimeExpression,
    NumberExpression,
    StringExpression,
    TimeExpression,
)


@dataclass
class BooleanAnyExpression:
    """Untyped wrapper for a boolean expression."""

    expr: BooleanExpression


@dataclass
class DateAnyExpression:
    """Untyped wrapper for a date expression."""

    expr: DateExpression


@dataclass
class DateTimeAnyExpression:
    """Untyped wrapper for a date-time expression."""

    expr: DateTimeExpression


@dataclass
class DirectedGroupOrdering:
    """Group ordering according to a given direction and type."""

    direction: "Direction"
    type: "GroupOrderingType"


class Direction(Enum):
    """Direction for ordering query results."""

    ASC = auto()
    DESC = auto()


@dataclass
class DirectLinkGroupByQuery:
    """Subquery targeting groups of directly linked entities."""

    alias: str
    condition: BooleanExpression
    entity_type: str
    group_by: List["Grouping"]
    link_alias: str
    source_id: int


@dataclass
class DirectLinkQuery:
    """Subquery targeting directly linked entities."""

    alias: str
    condition: BooleanExpression
    direct_link_group_by_queries: List[DirectLinkGroupByQuery]
    direct_link_queries: List["DirectLinkQuery"]
    entity_type: str
    include: List["AnyExpression"]
    limit: int
    link_alias: str
    link_group_by_queries: List["LinkGroupByQuery"]
    link_queries: List["Query"]
    offset: int
    order_by: List["Ordering"]
    source_id: int


@dataclass
class Grouping:
    """Query clause indicating how to group results."""

    key: "AnyExpression"
    ordering: "GroupOrdering"


class GroupOrderingType(Enum):
    """Type indicating which property to use for ordering result groups."""

    COUNT = auto()
    LABEL = auto()


@dataclass
class LinkGroupByQuery:
    """Subquery targeting groups of linked entities."""

    alias: str
    condition: BooleanExpression
    entity_type: str
    group_by: List[Grouping]
    source_id: int


@dataclass
class NumberAnyExpression:
    """Untyped wrapper for a number expression."""

    expr: NumberExpression


@dataclass
class Ordering:
    """Query clause indicating how to order results."""

    any_expression: "AnyExpression"
    direction: Direction


@dataclass
class Query:
    """Base query targeting linked or top-level entities."""

    alias: str
    condition: BooleanExpression
    direct_link_group_by_queries: List[DirectLinkGroupByQuery]
    direct_link_queries: List[DirectLinkQuery]
    entity_type: str
    include: List["AnyExpression"]
    limit: int
    link_group_by_queries: List[LinkGroupByQuery]
    link_queries: List["Query"]
    offset: int
    order_by: List[Ordering]
    source_id: int


@dataclass
class StringAnyExpression:
    """Untyped wrapper for a string expression."""

    expr: StringExpression


@dataclass
class TimeAnyExpression:
    """Untyped wrapper for a time expression."""

    expr: TimeExpression


AnyExpression = Union[
    BooleanAnyExpression,
    DateAnyExpression,
    DateTimeAnyExpression,
    NumberAnyExpression,
    StringAnyExpression,
    TimeAnyExpression,
]


@dataclass
class UnspecifiedGroupOrdering:
    """Sentinel value representing an unspecified group ordering."""

    pass


GroupOrdering = Union[DirectedGroupOrdering, UnspecifiedGroupOrdering]
