from typing import List

from elimity_insights_client.api._api import Config
from elimity_insights_client.api._api import query as api_query
from elimity_insights_client.api._api import sources
from elimity_insights_client.api.entities._entity import Entity, EntityType
from elimity_insights_client.api.entities._parse_query_results_page import (
    parse_query_results_page,
)
from elimity_insights_client.api.entities._query import query


def entities(config: Config, entity_type: EntityType) -> List[Entity]:
    """
    List all entities of the given entity type from the given source.

    The resulting entities also include all attribute assignments, and links for every other entity type of the given
    source.
    """

    sos = sources(config)
    schemas = {source.id: source.domain_graph_schema for source in sos}
    que = query(entity_type, schemas)
    queries = [que]
    (page,) = api_query(config, queries)
    return parse_query_results_page(entity_type, page, schemas)
