from networkx import Graph
import pytest
from tests.factory import *
from model.network.mobility_network import MobilityNetwork, \
    MNGeneratorFromFile, MNGeneratorFromNetworkData

BASELINE = 3
N = 1000
SEED = 1
PRE = create_network_data()
POST = create_network_data(True)

PRE.create_adjacency_list()
PRE.create_cum_prob()

POST.create_adjacency_list()
POST.create_cum_prob()

POST.calc_trip_count_change(PRE)


def test_create_network_instance():
    network = MobilityNetwork(PRE, N, BASELINE, False, SEED)
    assert isinstance(network, MobilityNetwork)


def test_network_create():
    network = MobilityNetwork(PRE, N, BASELINE, False, SEED)
    network.create()
    g = network.g
    assert isinstance(g, Graph)


def test_raises_value_error():
    with pytest.raises(ValueError):
        _ = MobilityNetwork(PRE, N, BASELINE, True, seed=SEED)


def test_create_households():
    # setup
    network = MobilityNetwork(PRE, N, BASELINE, False, SEED)

    # test
    households = network._create_households()

    assert abs(len(network.g.nodes) - N) < N / 10

    num_exceeds_std = 0
    for household in households:

        nodes = list(household.nodes)
        cbg = network.g.nodes[nodes[0]]['cbg']
        size_is = household.order()
        size_should = PRE.demographics[cbg]['household_size']

        if abs(size_is - size_should) > size_should / 2:
            num_exceeds_std += 1

    # normal distribution should exceed std in only 32% of cases
    assert num_exceeds_std < 0.32 * len(households)

    # todo test node proportion equals population proportion


def test_create_stubs():
    # setup
    network = MobilityNetwork(PRE, N, BASELINE, False, SEED)
    households = network._create_households()

    # test
    stubs, cbg_degree_map = network._create_stubs(households)

    # number of stubs
    num_nodes = len(stubs) + len(network.g.nodes)
    assert abs(num_nodes - N*BASELINE) < N
    assert len(stubs) % 2 == 0


def test_create_stub_pairs():
    network = MobilityNetwork(PRE, N, BASELINE, False, SEED)
    households = network._create_households()
    stubs, cbg_degree_map = network._create_stubs(households)

    # test
    stubs = network._create_stub_pairs(stubs, cbg_degree_map)

    assert len(stubs) % 2 == 0
    # todo add some more useful tests


def test_break_up_pairs():
    # setup
    network = MobilityNetwork(PRE, N, BASELINE, False, SEED)
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
    network = MobilityNetwork(PRE, N, BASELINE, False, SEED)
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
        MNGeneratorFromNetworkData.BASELINE: BASELINE,
        MNGeneratorFromNetworkData.MULTIPLIER: False,
        MNGeneratorFromNetworkData.SEED: SEED
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
