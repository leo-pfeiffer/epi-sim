import pytest
from lib.tests.factory import create_network_graph
from networkx import write_graphml


@pytest.fixture(scope="session")
def network_graph_file(tmpdir_factory):
    g = create_network_graph()
    fn = tmpdir_factory.mktemp("graphs").join("graph.graphml")
    write_graphml(g, str(fn))
    return fn
