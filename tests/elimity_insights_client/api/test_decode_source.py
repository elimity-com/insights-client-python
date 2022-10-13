from importlib.resources import open_binary
from json import load
from datetime import datetime
from typing import List

from dateutil.tz import tzoffset

from elimity_insights_client._domain_graph_schema import (
    AttributeType,
    EntityType,
    DomainGraphSchema,
    Type,
    RelationshipAttributeType,
)
from elimity_insights_client.api._decode_source import decode_source
from elimity_insights_client.api.source import Source, PresentLastReloadTimestamp


def test_decode_source() -> None:
    attribute_type = AttributeType(False, "baz", "foo", "foo", "bar", Type.STRING)
    attribute_types = [attribute_type]
    entity_type = EntityType(True, "baz", "foo", "bars", "bar")
    entity_types = [entity_type]
    relationship_attribute_types: List[RelationshipAttributeType] = []
    schema = DomainGraphSchema(
        attribute_types, entity_types, relationship_attribute_types
    )
    tzinfo = tzoffset(None, 25200)
    dat = datetime(2006, 5, 4, 3, 2, 1, tzinfo=tzinfo)
    timestamp = PresentLastReloadTimestamp(dat)
    source_file = open_binary(__package__, "source.json")
    source_json = load(source_file)
    assert Source(True, schema, 42, timestamp, "foo") == decode_source(source_json)
