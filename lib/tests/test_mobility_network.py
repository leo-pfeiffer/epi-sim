from networkx import Graph
import pytest
from lib.model.distributions import PowerLawCutoffDist, discrete_trunc_normal
from lib.model.network.mobility_network import MobilityNetwork, \
    MNGeneratorFromFile, MNGeneratorFromNetworkData
from lib.tests.factory import create_network_data

EXPONENT = 2
CUTOFF = 10
N = 1000
PRE = create_network_data()
POST = create_network_data(True)

PRE.create_adjacency_list()
PRE.create_cum_prob()

POST.create_adjacency_list()
POST.create_cum_prob()

POST.calc_trip_count_change(PRE)

DEGREE_DIST = PowerLawCutoffDist(EXPONENT, CUTOFF).p


def test_create_network_instance():
    network = MobilityNetwork(PRE, DEGREE_DIST, N, False)
    assert isinstance(network, MobilityNetwork)


def test_network_create_pre():
    network = MobilityNetwork(PRE, DEGREE_DIST, N, False)
    network.create()
    assert isinstance(network.g, Graph)
    assert N <= network.g.order() <= N * 1.1


def test_network_create_post():
    network = MobilityNetwork(POST, DEGREE_DIST, N, True)
    network.create()
    g = network.g
    assert isinstance(g, Graph)


def test_raises_value_error():
    with pytest.raises(ValueError):
        _ = MobilityNetwork(PRE, DEGREE_DIST, N, True)


def test_create_households():
    # setup
    network = MobilityNetwork(PRE, DEGREE_DIST, N, False)

    # test
    households = network._create_households()

    # number of nodes
    assert len(network.g.nodes) < N * 1.1

    num_exceeds_std = 0
    for household in households:

        nodes = list(household.nodes)
        cbg = network.g.nodes[nodes[0]]['cbg']
        size_is = household.order()
        size_should = PRE.demographics[cbg]['household_size']

        if abs(size_is - size_should) > size_should / 2:
            num_exceeds_std += 1

    # normal distribution should exceed std in only 32% of cases, ... but
    #  with some levy it is allowed in 45% of cases
    assert num_exceeds_std < 0.45 * len(households)


def test_create_stubs():
    # setup
    network = MobilityNetwork(PRE, DEGREE_DIST, N, False)
    households = network._create_households()

    # test
    stubs, cbg_degree_map = network._create_stubs(households)

    # number of stubs
    assert len(stubs) % 2 == 0


def test_create_stub_pairs():
    network = MobilityNetwork(PRE, DEGREE_DIST, N, False)
    households = network._create_households()
    stubs, cbg_degree_map = network._create_stubs(households)

    # test
    stubs = network._create_stub_pairs(stubs, cbg_degree_map)

    assert len(stubs) % 2 == 0


def test_break_up_pairs():
    # setup
    network = MobilityNetwork(PRE, DEGREE_DIST, N, False)
    households = network._create_households()
    stubs, cbg_degree_map = network._create_stubs(households)
    stubs = network._create_stub_pairs(stubs, cbg_degree_map)

    # test
    network._break_up_pairs(stubs)

    for i in range(0, len(stubs), 2):
        h1 = network.g.nodes[stubs[i]]['household']
        h2 = network.g.nodes[stubs[i + 1]]['household']
        assert h1 != h2


def test_connect_stubs():
    # setup
    network = MobilityNetwork(PRE, DEGREE_DIST, N, False)
    households = network._create_households()
    stubs, cbg_degree_map = network._create_stubs(households)
    stubs = network._create_stub_pairs(stubs, cbg_degree_map)
    stubs = network._break_up_pairs(stubs)

    # test
    network._connect_stubs(stubs)

    for i in range(0, len(stubs), 2):
        assert (stubs[i], stubs[i+1]) in network.g.edges


def test_mobility_network_generator_from_network_data():
    params = {
        MNGeneratorFromNetworkData.NETWORK_DATA: PRE,
        MNGeneratorFromNetworkData.N: N,
        MNGeneratorFromNetworkData.EXPONENT: EXPONENT,
        MNGeneratorFromNetworkData.CUTOFF: CUTOFF,
        MNGeneratorFromNetworkData.MULTIPLIER: False,
    }

    mng = MNGeneratorFromNetworkData(params=params)
    g = mng.generate()
    assert isinstance(g, Graph)


def test_mobility_network_generator_from_graph(network_graph_file):
    params = {
        MNGeneratorFromFile.PATH: str(network_graph_file),
    }

    mng = MNGeneratorFromFile(params=params)
    g = mng.generate()
    assert isinstance(g, Graph)
