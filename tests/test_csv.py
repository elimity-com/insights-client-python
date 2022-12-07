from importlib.resources import read_binary, read_text
from pickle import loads
from tempfile import TemporaryDirectory

from elimity_insights_client.csv import write_domain_graph


def test_csv() -> None:
    expected = _read_text("graph.csv")
    graph_file = read_binary(__package__, "graph.pickle")
    graph = loads(graph_file)
    schema_file = _read_text("schema.json")
    with TemporaryDirectory() as dir:
        filename = dir + "/graph.csv"
        write_domain_graph(filename, graph, schema_file)
        with open(filename) as file:
            actual = file.read()
    assert expected == actual


def _read_text(filename: str) -> str:
    return read_text(__package__, filename)
