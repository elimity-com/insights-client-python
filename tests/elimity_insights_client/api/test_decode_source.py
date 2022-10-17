from datetime import datetime
from typing import List

from dateutil.tz import tzoffset

from elimity_insights_client._domain_graph_schema import (
    AttributeType,
    DomainGraphSchema,
    EntityType,
    RelationshipAttributeType,
    Type,
)
from elimity_insights_client.api._decode_source import SourceDict, decode_source
from elimity_insights_client.api.source import PresentLastReloadTimestamp, Source
from tests.elimity_insights_client.api._json import (
    decode_file_local as json_decode_file_local,
)


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
    json = json_decode_file_local("source.json", SourceDict)
    assert Source(True, schema, 42, timestamp, "foo") == decode_source(json)
