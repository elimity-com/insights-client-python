"""Type definitions for expressions."""

from dataclasses import dataclass
from datetime import date, datetime, time
from enum import Enum, auto
from typing import List, Union


@dataclass
class ActiveBooleanExpression:
    """Expression evaluating whether a given entity is active."""

    reference: str


class AggregateOperator(Enum):
    """Operator to use when aggregating numeric expression results across entities."""

    AVG = auto()
    COUNT = auto()
    MAX = auto()
    MIN = auto()
    SUM = auto()


@dataclass
class AllBooleanExpression:
    """Expression evaluating whether all given sub-expressions hold."""

    exprs: List["BooleanExpression"]


@dataclass
class AnyBooleanExpression:
    """Expression evaluating whether any given sub-expression hold."""

    exprs: List["BooleanExpression"]


@dataclass
class AssignedBooleanExpression:
    """Expression evaluating whether a given attribute is assigned for a given entity."""

    attribute_type: str
    reference: str


@dataclass
class AttributeBooleanExpression:
    """Expression evaluating an attribute assignment for a given boolean attribute and entity."""

    attribute_type: str
    reference: str


@dataclass
class AttributeDateExpression:
    """Expression evaluating an attribute assignment for a given date attribute and entity."""

    attribute_type: str
    reference: str


@dataclass
class AttributeDateTimeExpression:
    """Expression evaluating an attribute assignment for a given date-time attribute and entity."""

    attribute_type: str
    reference: str


@dataclass
class AttributeNumberExpression:
    """Expression evaluating an attribute assignment for a given number attribute and entity."""

    attribute_type: str
    reference: str


@dataclass
class AttributeStringExpression:
    """Expression evaluating an attribute assignment for a given string attribute and entity."""

    attribute_type: str
    reference: str


@dataclass
class AttributeTimeExpression:
    """Expression evaluating an attribute assignment for a given time attribute and entity."""

    attribute_type: str
    reference: str


class CmpOperator(Enum):
    """Operator for binary comparisons."""

    EQ = auto()
    GT = auto()
    GTE = auto()
    LT = auto()
    LTE = auto()
    NEQ = auto()


@dataclass
class DateCmpBooleanExpression:
    """Expression evaluating to a comparison between results of two date expressions."""

    lhs: "DateExpression"
    operator: CmpOperator
    rhs: "DateExpression"


@dataclass
class DateTimeCmpBooleanExpression:
    """Expression evaluating to a comparison between results of two date-time expressions."""

    lhs: "DateTimeExpression"
    operator: CmpOperator
    rhs: "DateTimeExpression"


@dataclass
class DirectlyLinkedToBooleanExpression:
    """Expression evaluating whether a given entity is directly linked to some other entity matching a condition."""

    alias: str
    condition: "BooleanExpression"
    entity_type: str
    link_alias: str
    source_id: int


@dataclass
class DirectLinkAggregateNumberExpression:
    """Expression evaluating a given aggregate across a given entity's direct links."""

    alias: str
    condition: "BooleanExpression"
    entity_type: str
    expr: "NumberExpression"
    link_alias: str
    op: AggregateOperator
    source_id: int


@dataclass
class IdInBooleanExpression:
    """Expression evaluating whether an entity's identifier occurs in a given list."""

    ids: List[str]
    reference: str


@dataclass
class IdStringExpression:
    """Expression evaluating to a given entity's identifier."""

    reference: str


@dataclass
class LinkedToBooleanExpression:
    """Expression evaluating whether a given entity is linked to some other entity matching a given condition."""

    alias: str
    condition: "BooleanExpression"
    entity_type: str
    source_id: int


@dataclass
class LinkAggregateNumberExpression:
    """Expression evaluating a given aggregate across a given entity's links."""

    alias: str
    condition: "BooleanExpression"
    entity_type: str
    expr: "NumberExpression"
    op: AggregateOperator
    source_id: int


@dataclass
class LinkAssignedBooleanExpression:
    """Expression evaluating whether a given relationship attribute is assigned for a given link."""

    link_attribute_type: str
    link_reference: str


@dataclass
class LinkAttributeBooleanExpression:
    """Expression evaluating an attribute assignment for a given boolean attribute and link."""

    link_attribute_type: str
    link_reference: str


@dataclass
class LinkAttributeDateExpression:
    """Expression evaluating an attribute assignment for a given date attribute and link."""

    link_attribute_type: str
    link_reference: str


@dataclass
class LinkAttributeDateTimeExpression:
    """Expression evaluating an attribute assignment for a given date-time attribute and link."""

    link_attribute_type: str
    link_reference: str


@dataclass
class LinkAttributeNumberExpression:
    """Expression evaluating an attribute assignment for a given number attribute and link."""

    link_attribute_type: str
    link_reference: str


@dataclass
class LinkAttributeStringExpression:
    """Expression evaluating an attribute assignment for a given string attribute and link."""

    link_attribute_type: str
    link_reference: str


@dataclass
class LinkAttributeTimeExpression:
    """Expression evaluating an attribute assignment for a given time attribute and link."""

    link_attribute_type: str
    link_reference: str


@dataclass
class LiteralBooleanExpression:
    """Expression evaluating to a given boolean literal."""

    boolean: bool


@dataclass
class LiteralDateExpression:
    """Expression evaluating to a given date literal."""

    date: date


@dataclass
class LiteralDateTimeExpression:
    """Expression evaluating to a given date-time literal."""

    date_time: datetime


@dataclass
class LiteralNumberExpression:
    """Expression evaluating to a given number literal."""

    number: float


@dataclass
class LiteralStringExpression:
    """Expression evaluating to a given string literal."""

    string: str


@dataclass
class LiteralTimeExpression:
    """Expression evaluating to a given time literal."""

    time: time


@dataclass
class MatchBooleanExpression:
    """Expression evaluating to a match between results of two given string expressions."""

    lhs: "StringExpression"
    mode: "MatchMode"
    operator: "MatchOperator"
    rhs: "StringExpression"


class MatchMode(Enum):
    """Case-sensitivity mode for matching two strings."""

    CASE_INSENSITIVE = auto()
    CASE_SENSITIVE = auto()


class MatchOperator(Enum):
    """Operator for matching two strings."""

    CONTAINS = auto()
    ENDS_WITH = auto()
    EQUALS = auto()
    STARTS_WITH = auto()


@dataclass
class NameStringExpression:
    """Expression evaluating to a given entity's name."""

    reference: str


@dataclass
class NotBooleanExpression:
    """Expression evaluating to the boolean negation of a given expression's result."""

    expr: "BooleanExpression"


@dataclass
class NumberCmpBooleanExpression:
    """Expression evaluating to a comparison between results of two number expressions."""

    lhs: "NumberExpression"
    operator: CmpOperator
    rhs: "NumberExpression"


NumberExpression = Union[
    AttributeNumberExpression,
    DirectLinkAggregateNumberExpression,
    LinkAggregateNumberExpression,
    LinkAttributeNumberExpression,
    LiteralNumberExpression,
]


@dataclass
class RelativeDateExpression:
    """Expression representing a date offset from a current timestamp."""

    days: int
    future: bool
    months: int
    years: int


DateExpression = Union[
    AttributeDateExpression,
    LinkAttributeDateExpression,
    LiteralDateExpression,
    RelativeDateExpression,
]


@dataclass
class RelativeDateTimeExpression:
    """Expression representing a date-time offset from a current timestamp."""

    days: int
    hours: int
    future: bool
    minutes: int
    months: int
    seconds: int
    years: int


DateTimeExpression = Union[
    AttributeDateTimeExpression,
    LinkAttributeDateTimeExpression,
    LiteralDateTimeExpression,
    RelativeDateTimeExpression,
]

StringExpression = Union[
    AttributeStringExpression,
    IdStringExpression,
    LinkAttributeStringExpression,
    LiteralStringExpression,
    NameStringExpression,
]


@dataclass
class TimeCmpBooleanExpression:
    """Expression evaluating to a comparison between results of two time expressions."""

    lhs: "TimeExpression"
    operator: CmpOperator
    rhs: "TimeExpression"


BooleanExpression = Union[
    ActiveBooleanExpression,
    AllBooleanExpression,
    AnyBooleanExpression,
    AssignedBooleanExpression,
    AttributeBooleanExpression,
    DateCmpBooleanExpression,
    DateTimeCmpBooleanExpression,
    DirectlyLinkedToBooleanExpression,
    IdInBooleanExpression,
    LinkAssignedBooleanExpression,
    LinkAttributeBooleanExpression,
    LinkedToBooleanExpression,
    LiteralBooleanExpression,
    MatchBooleanExpression,
    NotBooleanExpression,
    NumberCmpBooleanExpression,
    TimeCmpBooleanExpression,
]

TimeExpression = Union[
    AttributeTimeExpression,
    LinkAttributeTimeExpression,
    LiteralTimeExpression,
]
