"""Utilities for writing domain graph schemas to CSV files."""

from collections.abc import Iterable
from csv import writer
from json import dumps, loads

from elimity_insights_client._decode_domain_graph_schema import (
    decode_domain_graph_schema,
)
from elimity_insights_client._domain_graph_schema import DomainGraphSchema
from elimity_insights_client._elimity_insights_client import (
    BooleanValue,
    DateTimeValue,
    DateValue,
    DomainGraph,
    Entity,
    NumberValue,
    Relationship,
    StringValue,
    Value,
)


def write_domain_graph(filename: str, graph: DomainGraph, schema_json: str) -> None:
    """Serialize the given domain graph to an importable CSV file at the given path."""
    schema_dict = loads(schema_json)
    schema = decode_domain_graph_schema(schema_dict)
    with open(filename, "w", newline="") as file:
        wri = writer(file)
        rows = _rows(graph, schema)
        wri.writerows(rows)


def _rows(graph: DomainGraph, schema: DomainGraphSchema) -> Iterable[Iterable[str]]:
    yield _headers(schema)
    for entity in graph.entities:
        yield _entity_cells(entity, schema)
    for relationship in graph.relationships:
        yield _relationship_cells(relationship, schema)


def _headers(schema: DomainGraphSchema) -> Iterable[str]:
    for entity_type in schema.entity_types:
        id = entity_type.id
        yield from [id + ": id", id + ": name"]
    for attribute_type in schema.attribute_types:
        yield f"{attribute_type.entity_type}: {attribute_type.id}"


def _entity_cells(entity: Entity, schema: DomainGraphSchema) -> Iterable[str]:
    type = entity.type
    for entity_type in schema.entity_types:
        yield from [entity.id, entity.name] if entity_type.id == type else ["", ""]
    values = {
        assignment.attribute_type_id: assignment.value
        for assignment in entity.attribute_assignments
    }
    for attribute_type in schema.attribute_types:
        value = values.get(attribute_type.id)
        yield "" if attribute_type.entity_type != type or value is None else _cell(
            value
        )


def _relationship_cells(
    relationship: Relationship, schema: DomainGraphSchema
) -> Iterable[str]:
    for type in schema.entity_types:
        dict = {
            relationship.from_entity_type: relationship.from_entity_id,
            relationship.to_entity_type: relationship.to_entity_id,
        }
        yield dict.get(type.id, "")
        yield ""
    yield from [""] * len(schema.attribute_types)


def _cell(value: Value) -> str:
    if isinstance(value, BooleanValue):
        return "true" if value.value else "false"

    elif isinstance(value, DateValue):
        return f"{value.year:04}-{value.month:02}-{value.day:02}"

    elif isinstance(value, DateTimeValue):
        val = value.value
        return f"{val.year:04}-{val.month:02}-{val.day:02} {val.hour:02}:{val.minute:02}:{val.second:02}.0"

    elif isinstance(value, NumberValue):
        return dumps(value.value)

    elif isinstance(value, StringValue):
        return value.value

    else:
        return f"{value.hour:02}:{value.minute:02}:{value.second:02}.0"
