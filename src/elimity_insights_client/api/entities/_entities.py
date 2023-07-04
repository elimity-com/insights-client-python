from typing import List, Optional, Set

from elimity_insights_client.api._api import Config
from elimity_insights_client.api._api import query as api_query
from elimity_insights_client.api._api import sources
from elimity_insights_client.api.entities._entity import Entity, EntityType
from elimity_insights_client.api.entities._parse_query_results_page import (
    parse_query_results_page,
)
from elimity_insights_client.api.entities._query import query


def entities(
    config: Config,
    entity_type: EntityType,
    linked_source_ids: Optional[Set[int]] = None,
) -> List[Entity]:
    """
    List all entities of the given entity type from the given source.

    The resulting entities also include all attribute assignments, and links for every other entity type
    of one of the given linked sources. If linked_source_ids is None, then all other existing sources are used.
    """

    sos = sources(config)
    schemas = {
        source.id: source.domain_graph_schema
        for source in sos
        if source.id == entity_type.source_id or linked_source_ids is None or source.id in linked_source_ids
    }
    que = query(entity_type, schemas)
    queries = [que]
    (page,) = api_query(config, queries)
    return parse_query_results_page(entity_type, page, schemas)
