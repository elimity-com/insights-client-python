from datetime import date, datetime
from json import loads
from typing import List

from dateutil.parser import isoparse, isoparser
from typing_extensions import TypedDict

from elimity_insights_client._util import map_list
from elimity_insights_client.api.query_results_page import (
    BooleanValue,
    DateTimeValue,
    DateValue,
    Entity,
    GroupByQueryResult,
    GroupByQueryResultsPage,
    NumberValue,
    QueryResult,
    QueryResultsPage,
    StringValue,
    TimeValue,
    Value,
)


class EntityDict(TypedDict):
    active: bool
    id: str
    name: str


class GroupByQueryResultsPageDict(TypedDict):
    groupCount: int
    results: List["GroupByQueryResultDict"]


class GroupByQueryResultDict(TypedDict):
    count: int
    label: "ValueDict"
    subPages: List[GroupByQueryResultsPageDict]


class QueryResultsPageDict(TypedDict):
    count: int
    results: List["QueryResultDict"]


class QueryResultDict(TypedDict):
    entity: EntityDict
    inclusions: List["ValueDict"]
    linkGroupByPages: List[GroupByQueryResultsPageDict]
    linkPages: List[QueryResultsPageDict]


class ValueDict(TypedDict):
    type: str
    value: str


def decode_query_results_page(dict: QueryResultsPageDict) -> QueryResultsPage:
    count = dict["count"]
    result_dicts = dict["results"]
    results = map_list(_decode_query_result, result_dicts)
    return QueryResultsPage(count, results)


def _decode_group_by_query_result(dict: GroupByQueryResultDict) -> GroupByQueryResult:
    count = dict["count"]
    label_dict = dict["label"]
    label = _decode_value(label_dict)
    sub_page_dicts = dict["subPages"]
    sub_pages = map_list(_decode_group_by_query_results_page, sub_page_dicts)
    return GroupByQueryResult(count, label, sub_pages)


def _decode_group_by_query_results_page(
    dict: GroupByQueryResultsPageDict,
) -> GroupByQueryResultsPage:
    group_count = dict["groupCount"]
    result_dicts = dict["results"]
    results = map_list(_decode_group_by_query_result, result_dicts)
    return GroupByQueryResultsPage(group_count, results)


def _decode_query_result(dict: QueryResultDict) -> QueryResult:
    entity_dict = dict["entity"]
    active = entity_dict["active"]
    id = entity_dict["id"]
    name = entity_dict["name"]
    entity = Entity(active, id, name)
    inclusion_dicts = dict["inclusions"]
    inclusions = map_list(_decode_value, inclusion_dicts)
    link_group_by_page_dicts = dict["linkGroupByPages"]
    link_group_by_pages = map_list(
        _decode_group_by_query_results_page, link_group_by_page_dicts
    )
    link_page_dicts = dict["linkPages"]
    link_pages = map_list(decode_query_results_page, link_page_dicts)
    return QueryResult(entity, inclusions, link_group_by_pages, link_pages)


def _decode_value(dict: ValueDict) -> Value:
    type = dict["type"]
    value = dict["value"]
    if type == "boolean":
        return BooleanValue(value == "true")

    if type == "date":
        date_value = _parse_date(value)
        return DateValue(date_value)

    if type == "dateTime":
        date_time_value = _parse_datetime(value)
        return DateTimeValue(date_time_value)

    if type == "number":
        number_value = loads(value)
        return NumberValue(number_value)

    if type == "string":
        return StringValue(value)

    parser = isoparser()
    time_value = parser.parse_isotime(value)
    return TimeValue(time_value)


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.min


def _parse_datetime(value: str) -> datetime:
    try:
        return isoparse(value)
    except ValueError:
        return datetime.min
