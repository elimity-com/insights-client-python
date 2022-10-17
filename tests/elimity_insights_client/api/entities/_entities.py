from typing import Type, TypeVar

from elimity_insights_client._decode_domain_graph_schema import (
    DomainGraphSchemaDict,
    decode_domain_graph_schema,
)
from tests.elimity_insights_client.api._json import decode_file as json_decode_file

_T = TypeVar("_T")


def json_decode_file_local(filename: str, type: Type[_T]) -> _T:
    return json_decode_file(filename, __package__, type)


_json = json_decode_file_local("schema.json", DomainGraphSchemaDict)
schema = decode_domain_graph_schema(_json)
