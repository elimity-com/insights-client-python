from typing import List, Tuple, Type, TypedDict, TypeVar

from elimity_insights_client._decode_domain_graph_schema import (
    DomainGraphSchemaDict,
    decode_domain_graph_schema,
)
from elimity_insights_client._domain_graph_schema import DomainGraphSchema
from elimity_insights_client.api.entities._entity import EntityType
from tests.elimity_insights_client.api._json import decode_file as json_decode_file

_T = TypeVar("_T")

_SourceDict = TypedDict(
    "_SourceDict",
    {
        "schema": DomainGraphSchemaDict,
        "sourceId": int,
    },
)


def json_decode_file_local(filename: str, type: Type[_T]) -> _T:
    return json_decode_file(filename, __package__, type)


def _item(dict: _SourceDict) -> Tuple[int, DomainGraphSchema]:
    schema = dict["schema"]
    return dict["sourceId"], decode_domain_graph_schema(schema)


_json = json_decode_file_local("sources.json", List[_SourceDict])
_items = map(_item, _json)
schemas = dict(_items)

type = EntityType("foo", 42)
