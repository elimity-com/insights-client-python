from importlib.resources import open_binary
from json import load, loads
from typing import Type, TypeVar, cast

from simplejson import dumps

from elimity_insights_client.api._encode_query import encode_query
from elimity_insights_client.api.query import Query

_T = TypeVar("_T")


def decode_file(filename: str, package: str, _type: Type[_T]) -> _T:
    file = open_binary(package, filename)
    json = load(file)
    return cast(_T, json)


def decode_file_local(filename: str, type: Type[_T]) -> _T:
    return decode_file(filename, __package__, type)


def encode_query_list(query: Query) -> object:
    json = encode_query(query)
    str = dumps(json, iterable_as_array=True)
    return loads(str)
