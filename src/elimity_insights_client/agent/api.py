"""API endpoints for agent interactions with an Elimity Insights server."""

from dataclasses import dataclass
from typing import List, TypeVar, cast, Type, Optional

from requests import request

from elimity_insights_client._util import encoder, map_list
from elimity_insights_client.agent._decode_query_results_page import (
    decode_query_results_page,
    QueryResultsPageDict,
)
from elimity_insights_client.agent._decode_source import SourceDict, decode_source
from elimity_insights_client.agent.query import Query
from elimity_insights_client.agent.query_results_page import QueryResultsPage
from elimity_insights_client.agent._encode_query import encode_query
from elimity_insights_client.agent.source import Source


@dataclass
class Config:
    """Configuration consisting of agent credentials and connection properties."""

    token_id: str
    token_secret: str
    url: str
    verify_ssl: bool


_T = TypeVar("_T")


def query(config: Config, queries: List[Query]) -> List[QueryResultsPage]:
    """Perform the given queries and return the result pages."""
    query_iter = map(encode_query, queries)
    data = encoder.encode(query_iter)
    page_dicts = _request(
        config, data, "POST", "/api/agent/query", List[QueryResultsPageDict]
    )
    return map_list(decode_query_results_page, page_dicts)


def sources(config: Config) -> List[Source]:
    """List all configured sources."""
    source_dicts = _request(config, None, "GET", "/api/agent/sources", List[SourceDict])
    return map_list(decode_source, source_dicts)


def _request(
    config: Config, data: Optional[str], method: str, path: str, _type: Type[_T]
) -> _T:
    auth = config.token_id, config.token_secret
    headers = {"Content-Type": "application/json"}
    response = request(
        method,
        config.url + path,
        auth=auth,
        data=data,
        headers=headers,
        verify=config.verify_ssl,
    )
    response.raise_for_status()
    json = response.json()
    return cast(_T, json)