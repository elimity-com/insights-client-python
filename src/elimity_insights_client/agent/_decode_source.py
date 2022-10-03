from typing import TypedDict, Optional

from typing_extensions import NotRequired

from elimity_insights_client._decode_domain_graph_schema import (
    DomainGraphSchemaDict,
    decode_domain_graph_schema,
)
from elimity_insights_client.agent.source import (
    Source,
    LastReloadTimestamp,
    AbsentLastReloadTimestamp,
    PresentLastReloadTimestamp,
)
from datetime import datetime


class SourceDict(TypedDict):
    """JSON value representing a source."""

    archived: bool
    domainGraphSchema: DomainGraphSchemaDict
    id: int
    lastReloadTimestamp: NotRequired[str]
    name: str


def decode_source(dict: SourceDict) -> Source:
    """Decode the given JSON value to a source."""
    archived = dict["archived"]
    domain_graph_schema_dict = dict["domainGraphSchema"]
    domain_graph_schema = decode_domain_graph_schema(domain_graph_schema_dict)
    id = dict["id"]
    last_reload_timestamp_json = dict.get("lastReloadTimestamp")
    last_reload_timestamp = _decode_last_reload_timestamp(last_reload_timestamp_json)
    name = dict["name"]
    return Source(archived, domain_graph_schema, id, last_reload_timestamp, name)


def _decode_last_reload_timestamp(value: Optional[str]) -> LastReloadTimestamp:
    if value is None:
        return AbsentLastReloadTimestamp()
    val = datetime.fromisoformat(value)
    return PresentLastReloadTimestamp(val)