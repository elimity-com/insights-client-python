"""Type definitions for sources."""

from dataclasses import dataclass
from datetime import datetime
from typing import Union

from elimity_insights_client._domain_graph_schema import DomainGraphSchema


@dataclass
class AbsentLastReloadTimestamp:
    """Sentinel value indicating a last reload timestamp is not applicable."""

    pass


@dataclass
class PresentLastReloadTimestamp:
    """Timestamp indicating when a source has been most recently reloaded."""

    value: datetime


LastReloadTimestamp = Union[AbsentLastReloadTimestamp, PresentLastReloadTimestamp]


@dataclass
class Source:
    """Source providing domain data to an Elimity Insights server."""

    archived: bool
    domain_graph_schema: DomainGraphSchema
    id: int
    last_reload_timestamp: LastReloadTimestamp
    name: str
