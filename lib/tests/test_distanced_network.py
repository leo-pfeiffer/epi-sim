from functools import partial
from networkx import Graph
import numpy as np

from lib.model.network.distanced_network import DistancedNetwork, DNGenerator
from lib.model.distributions import discrete_trunc_exponential, \
    discrete_trunc_normal, num_contact_dist


EXPONENT = 2
N = 1000
SEED = 1

HOUSEHOLD_SIZE = 4.5
average_family = partial(discrete_trunc_normal, mu=HOUSEHOLD_SIZE, std=2)
intra_family_contacts = partial(num_contact_dist, std=1)
inter_family_contacts = partial(discrete_trunc_exponential, exponent=EXPONENT)


def test_create_network():
    network = DistancedNetwork(N, average_family, intra_family_contacts,
                               inter_family_contacts)

    network.create()
    assert isinstance(network.g, Graph)
    assert N * 0.9 <= network.g.order() <= N * 1.1


def test_create_households():
    # setup
    network = DistancedNetwork(
        N, average_family, intra_family_contacts, inter_family_contacts
    )

    # test
    households = network._create_households()

    # number of nodes
    assert len(network.g.nodes) < N * 1.1

    num_exceeds_std = 0
    for household in households:

        size_is = household.order()

        if abs(size_is - HOUSEHOLD_SIZE) > HOUSEHOLD_SIZE / 2:
            num_exceeds_std += 1

    # normal distribution should exceed std in only 32% of cases, ... but
    #  with some levy it is allowed in 45% of cases
    assert num_exceeds_std < 0.45 * len(households)


def test_create_stubs():
    # setup
    network = DistancedNetwork(
        N, average_family, intra_family_contacts, inter_family_contacts
    )

    households = network._create_households()

    # test
    stubs = network._create_stubs(households)

    # number of stubs
    assert len(stubs) % 2 == 0

    # expected number of outside nodes
    avg_contacts = np.mean([num_contact_dist(h.order()) for h in households])
    exp_c_nodes = len(households) * avg_contacts
    is_c_nodes = len(set(stubs))

    # high threshold necessary cause it varies a lot...
    assert abs(1 - exp_c_nodes / is_c_nodes) < 0.4

    # expected number of stubs
    avg_connections = np.mean([inter_family_contacts() for _ in list(set(stubs))])
    exp_connections = is_c_nodes * avg_connections
    is_connections = len(stubs)

    # high threshold necessary cause it varies a lot...
    assert abs(1 - exp_connections / is_connections) < 0.4


def test_break_up_pairs():

    # setup
    network = DistancedNetwork(
        N, average_family, intra_family_contacts, inter_family_contacts
    )
    households = network._create_households()
    stubs = network._create_stubs(households)

    # test
    network._break_up_pairs(stubs)

    for i in range(0, len(stubs), 2):
        h1 = network.g.nodes[stubs[i]]['household']
        h2 = network.g.nodes[stubs[i + 1]]['household']
        assert h1 != h2


def test_connect_stubs():
    # setup
    # setup
    network = DistancedNetwork(
        N, average_family, intra_family_contacts, inter_family_contacts
    )
    households = network._create_households()
    stubs = network._create_stubs(households)
    stubs = network._break_up_pairs(stubs)

    # test
    network._connect_stubs(stubs)

    for i in range(0, len(stubs), 2):
        assert (stubs[i], stubs[i+1]) in network.g.edges


def test_distanced_generator():
    params = {
        DNGenerator.N: N,
        DNGenerator.HOUSEHOLD_SIZE_DIST: average_family,
        DNGenerator.NUM_CONTACT_DIST: intra_family_contacts,
        DNGenerator.NUM_OUTSIDE_EDGE_DIST: inter_family_contacts,
    }

    mng = DNGenerator(params=params)
    g = mng.generate()
    assert isinstance(g, Graph)
