from typing import Dict, List

from elimity_insights_client.api._decode_query_results_page import (
    QueryResultsPageDict,
    decode_query_results_page,
)
from elimity_insights_client.api.entities._entity import Entity, Link
from elimity_insights_client.api.entities._parse_query_results_page import (
    parse_query_results_page,
)
from elimity_insights_client.api.query_results_page import NumberValue, Value
from tests.elimity_insights_client.api.entities._entities import (
    json_decode_file_local,
    schema,
)


def test_parse_query_results_page() -> None:
    json = json_decode_file_local("query-results-page.json", QueryResultsPageDict)
    page = decode_query_results_page(json)
    value: Value = NumberValue(24)
    link_assignments = {"ipsum": value}
    link = Link(link_assignments, "baz", "lorem")
    entity_assignments: Dict[str, Value] = {}
    bar_links = [link]
    lorem_links: List[Link] = []
    entity_links = {"bar": bar_links, "lorem": lorem_links}
    entity = Entity(entity_assignments, "foo", entity_links, "bar")
    assert [entity] == parse_query_results_page("foo", page, schema)
