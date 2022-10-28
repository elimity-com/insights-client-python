from dataclasses import dataclass
from typing import Dict, List

from elimity_insights_client.api.query_results_page import Value


@dataclass
class Entity:
    """Single entity with assignments for all attributes and links for all entity types."""

    attribute_assignments: Dict[str, Value]
    id: str
    links: Dict["EntityType", List["Link"]]
    name: str


@dataclass(frozen=True)
class EntityType:
    """Type of entities for a given source, represents a unique key in dictionaries of links."""

    id: str
    source_id: int


@dataclass
class Link:
    """Linked entity with assignments for all attributes."""

    attribute_assignments: Dict[str, Value]
    id: str
    name: str
