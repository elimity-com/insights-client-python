from dataclasses import dataclass
from typing import Dict, List

from elimity_insights_client.api.query_results_page import Value


@dataclass
class Entity:
    """Single entity with assignments for all attributes and links for all entity types."""

    attribute_assignments: Dict[str, Value]
    id: str
    links: Dict[str, List["Link"]]
    name: str


@dataclass
class Link:
    """Linked entity with assignments for all attributes."""

    attribute_assignments: Dict[str, Value]
    id: str
    name: str
