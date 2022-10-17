from datetime import datetime
from typing import Callable, List, TypeVar

from dateutil.tz import tzlocal
from dateutil.utils import default_tzinfo
from simplejson import JSONEncoder

encoder = JSONEncoder(iterable_as_array=True)
local_timezone = tzlocal()

_T = TypeVar("_T")
_U = TypeVar("_U")


def encode_datetime(datetime: datetime) -> object:
    """Encode the given datetime to a JSON value."""
    dat = default_tzinfo(datetime, local_timezone)
    return dat.isoformat()


def map_list(callable: Callable[["_T"], "_U"], iterable: List["_T"]) -> List["_U"]:
    """Apply the given function to each item in the given list, and construct a new list from the results."""
    iterator = map(callable, iterable)
    return list(iterator)
