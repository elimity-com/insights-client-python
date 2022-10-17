from typing import Dict

from hypothesis import HealthCheck, given, settings
from jsonschema import validate

from elimity_insights_client.api.query import Query
from tests.elimity_insights_client.api._json import (
    decode_file_local as json_decode_file_local,
)
from tests.elimity_insights_client.api._json import (
    encode_query_list as json_encode_query_list,
)

_health_checks = [HealthCheck.too_slow]


@given(...)
@settings(deadline=None, derandomize=True, suppress_health_check=_health_checks)
def test_encode_query(query: Query) -> None:
    query_json = json_encode_query_list(query)
    schema_json = json_decode_file_local("schema.json", Dict[str, object])
    validate(query_json, schema_json)
