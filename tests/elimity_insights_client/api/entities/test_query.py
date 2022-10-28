from elimity_insights_client.api.entities._query import query
from tests.elimity_insights_client.api._json import (
    encode_query_list as json_encode_query_list,
)
from tests.elimity_insights_client.api.entities._entities import (
    json_decode_file_local,
    schemas,
    type,
)


def test_query() -> None:
    que = query(type, schemas)
    assert json_decode_file_local("query.json", object) == json_encode_query_list(que)
