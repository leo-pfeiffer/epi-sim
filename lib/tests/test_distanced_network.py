from functools import partial

from lib.model.network.distanced_network import DistancedNetwork
from lib.model.distributions import discrete_trunc_exponential, \
    discrete_trunc_normal, num_contact_dist

from networkx import Graph


EXPONENT = 2
N = 1000
SEED = 1

average_family = partial(discrete_trunc_normal, mu=4.5, std=2)
intra_family_contacts = partial(num_contact_dist, std=1)
inter_family_contacts = partial(discrete_trunc_exponential, exponent=EXPONENT)


def test_create_network():
    network = DistancedNetwork(N, average_family, intra_family_contacts,
                               inter_family_contacts)

    network.create()
    assert isinstance(network.g, Graph)
    assert network.g.order() >= N
