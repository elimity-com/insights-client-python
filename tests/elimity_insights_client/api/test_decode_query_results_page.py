from datetime import datetime, timezone
from importlib.resources import open_binary
from json import load
from typing import List

from elimity_insights_client.api._decode_query_results_page import (
    decode_query_results_page,
)
from elimity_insights_client.api.query_results_page import (
    BooleanValue,
    DateTimeValue,
    Entity,
    GroupByQueryResult,
    GroupByQueryResultsPage,
    NumberValue,
    QueryResult,
    QueryResultsPage,
    Value,
)


def test_decode_query_results_page() -> None:
    entity = Entity(True, "bar", "foo")
    inclusion1: Value = BooleanValue(False)
    dat = datetime(2006, 5, 4, 3, 2, 1, tzinfo=timezone.utc)
    inclusion2: Value = DateTimeValue(dat)
    inclusions = [inclusion1, inclusion2]
    label = NumberValue(42)
    sub_pages: List[GroupByQueryResultsPage] = []
    link_group_by_result = GroupByQueryResult(0, label, sub_pages)
    link_group_by_results = [link_group_by_result]
    link_group_by_page = GroupByQueryResultsPage(1, link_group_by_results)
    link_group_by_pages = [link_group_by_page]
    link_results: List[QueryResult] = []
    link_page = QueryResultsPage(0, link_results)
    link_pages = [link_page]
    result = QueryResult(entity, inclusions, link_group_by_pages, link_pages)
    results = [result]
    page_file = open_binary(__package__, "query-results-page.json")
    page_json = load(page_file)
    assert QueryResultsPage(1, results) == decode_query_results_page(page_json)
