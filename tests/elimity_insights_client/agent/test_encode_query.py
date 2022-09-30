from importlib.resources import open_binary
from json import load, loads

from hypothesis import given, settings, HealthCheck
from simplejson import dumps
from jsonschema import validate

from elimity_insights_client.agent._encode_query import encode_query
from elimity_insights_client.agent.query import Query

_health_checks = [HealthCheck.too_slow]


@given(...)
@settings(deadline=None, derandomize=True, suppress_health_check=_health_checks)
def test_encode_query(query: Query) -> None:
    query_iter_json = encode_query(query)
    query_str = dumps(query_iter_json, iterable_as_array=True)
    query_list_json = loads(query_str)
    schema_file = open_binary(__package__, "schema.json")
    schema_json = load(schema_file)
    validate(query_list_json, schema_json)
