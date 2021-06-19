import pytest
from tests.factory import *
from model.network import Network
from model.network_data import NetworkData

BASELINE = 3
N = 1000
SEED = 1
PRE = create_network_data()
POST = create_network_data(True)

PRE.create_adjacency_list()
PRE.create_cum_prob()

POST.create_adjacency_list()
POST.create_cum_prob()

TRIP_COUNT_CHANGE = NetworkData.calc_trip_count_change(PRE, POST)


def test_create_network_instance():
    network = Network(PRE, TRIP_COUNT_CHANGE, N, BASELINE, False, SEED)
    assert isinstance(network, Network)


def test_create_households():
    # setup
    network = Network(PRE, TRIP_COUNT_CHANGE, N, BASELINE, False, SEED)

    # test
    households, cbg_degree_map = network._create_households()

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
    network = Network(PRE, TRIP_COUNT_CHANGE, N, BASELINE, False, SEED)
    households, cbg_degree_map = network._create_households()

    # test
    stubs, cbg_degree_map = network._create_stubs(households, cbg_degree_map)

    # number of stubs
    num_nodes = len(stubs) + len(network.g.nodes)
    assert abs(num_nodes - N*BASELINE) < N
    assert len(stubs) % 2 == 0


def test_create_stub_pairs():
    network = Network(PRE, TRIP_COUNT_CHANGE, N, BASELINE, False, SEED)
    households, cbg_degree_map = network._create_households()
    stubs, cbg_degree_map = network._create_stubs(households, cbg_degree_map)

    # test
    stubs = network._create_stub_pairs(stubs, cbg_degree_map)

    assert len(stubs) % 2 == 0
    # todo add some more useful tests


def test_break_up_pairs():
    # setup
    network = Network(PRE, TRIP_COUNT_CHANGE, N, BASELINE, False, SEED)
    households, cbg_degree_map = network._create_households()
    stubs, cbg_degree_map = network._create_stubs(households, cbg_degree_map)
    stubs = network._create_stub_pairs(stubs, cbg_degree_map)

    # test
    network._break_up_pairs(stubs)

    for i in range(0, len(stubs), 2):
        h1 = network.g.nodes[stubs[i]]['household']
        h2 = network.g.nodes[stubs[i + 1]]['household']
        assert h1 != h2
