from dataclasses import dataclass
from enum import Enum, auto
from typing import List


@dataclass
class AttributeType:
    """Attribute type for an entity type."""

    archived: bool
    description: str
    entity_type: str
    id: str
    name: str
    type: "Type"


@dataclass
class DomainGraphSchema:
    """Schema determining valid domain graphs."""

    attribute_types: List[AttributeType]
    entity_types: List["EntityType"]
    relationship_attribute_types: List["RelationshipAttributeType"]


@dataclass
class EntityType:
    """Type of an entity."""

    anonymized: bool
    icon: str
    id: str
    plural: str
    singular: str


@dataclass
class RelationshipAttributeType:
    """Attribute type for relationships between entities of specific types."""

    archived: bool
    description: str
    from_entity_type: str
    id: str
    name: str
    to_entity_type: str
    type: "Type"


class Type(Enum):
    """Type of an attribute type, determining valid assignment values."""

    BOOLEAN = auto()
    DATE = auto()
    DATE_TIME = auto()
    NUMBER = auto()
    STRING = auto()
    TIME = auto()
