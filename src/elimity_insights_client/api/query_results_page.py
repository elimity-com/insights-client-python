"""Type definitions for query result pages."""

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import List, Union


@dataclass
class BooleanValue:
    """Typed wrapper for a boolean value."""

    value: bool


@dataclass
class DateValue:
    """Typed wrapper for a date value."""

    value: date


@dataclass
class DateTimeValue:
    """Typed wrapper for a date-time value."""

    value: datetime


@dataclass
class Entity:
    """Matched entity as part of a query result."""

    active: bool
    id: str
    name: str


@dataclass
class GroupByQueryResult:
    """Matched group as part of a group-by query result page."""

    count: int
    label: "Value"
    sub_pages: List["GroupByQueryResultsPage"]


@dataclass
class GroupByQueryResultsPage:
    """Page of results for a group-by query."""

    group_count: int
    results: List[GroupByQueryResult]


@dataclass
class NumberValue:
    """Typed wrapper for a number value."""

    value: float


@dataclass
class QueryResult:
    """Entry in a page of query results consisting of entity details, inclusions and sub-results."""

    entity: Entity
    inclusions: List["Value"]
    link_group_by_pages: List[GroupByQueryResultsPage]
    link_pages: List["QueryResultsPage"]


@dataclass
class QueryResultsPage:
    """Page of results for a query."""

    count: int
    results: List[QueryResult]


@dataclass
class StringValue:
    """Typed wrapper for a string value."""

    value: str


@dataclass
class TimeValue:
    """Typed wrapper for a time value."""

    value: time


Value = Union[
    BooleanValue, DateValue, DateTimeValue, NumberValue, StringValue, TimeValue
]
