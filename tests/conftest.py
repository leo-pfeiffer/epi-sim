import pytest
from model.network.power_law_cutoff import PowerLawCutoffNetwork
from tests.factory import create_network_graph
from networkx import write_graphml

@pytest.fixture()
def plc_distribution(tau=0.2, kappa=10):
    return PowerLawCutoffNetwork.distribution(tau=tau, kappa=kappa)


@pytest.fixture()
def plc(n=100, tau=0.2, kappa=10):
    params = {
        PowerLawCutoffNetwork.N: n,
        PowerLawCutoffNetwork.TAU: tau,
        PowerLawCutoffNetwork.KAPPA: kappa
    }
    return PowerLawCutoffNetwork(params)


@pytest.fixture(scope="session")
def network_graph_file(tmpdir_factory):
    g = create_network_graph()
    fn = tmpdir_factory.mktemp("graphs").join("graph.graphml")
    write_graphml(g, str(fn))
    return fn
