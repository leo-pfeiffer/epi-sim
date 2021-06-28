from functools import partial

from model.network.distanced_network import DistancedNetwork, DNGenerator
from model.distributions import node_degree_dist, household_size_dist, \
    intra_household_contacts

from networkx import Graph


EXPONENT = 2
N = 1000
SEED = 1

average_family = partial(household_size_dist, mu=4.5, std=2)
intra_family_contacts = partial(intra_household_contacts, std=1)
inter_family_contacts = partial(node_degree_dist, exponent=EXPONENT)


def test_create_network():
    network = DistancedNetwork(N, average_family, intra_family_contacts,
                               inter_family_contacts, SEED)

    network.create()
    assert isinstance(network.g, Graph)
    assert network.g.order() >= N
