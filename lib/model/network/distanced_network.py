import sys
from typing import Callable, Any, Dict, List
if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

import networkx as nx
import numpy as np
from epydemic import NetworkGenerator

# special types for convenience...
HOUSEHOLDS = List[nx.Graph]
STUBS = List[int]


# todo comments, docstrings, unit tests

class DistancedNetwork:
    """
    Implementation of the distanced network presented in
        Dobson 2020 - Epidemic Modelling, pp. 157
    """

    def __init__(self, N: int, household_size_dist: Callable,
                 num_contact_dist: Callable, num_outside_edge_dist: Callable):
        """
        Create a DistancedNetwork.
        :param N: Order of the network.
        :param household_size_dist: Distribution func. of household sizes.
        :param num_contact_dist: Distribution func. of number of household
            members with outside edges.
        :param num_outside_edge_dist: Distribution func. of number of outside
            edges for single member with outside edges
        """
        self.N = N
        self.household_size_dist = household_size_dist
        self.num_contact_dist = num_contact_dist
        self.num_outside_edge_dist = num_outside_edge_dist

        self._rng = np.random.default_rng()
        self._g: nx.Graph = nx.Graph()

    @property
    def g(self):
        return self._g

    def create(self):
        households = self._create_households()
        stubs = self._create_stubs(households)
        stubs = self._break_up_pairs(stubs)
        self._connect_stubs(stubs)

    def _create_households(self) -> HOUSEHOLDS:
        household_id = 1
        households = []
        n = 0

        while n < self.N:
            size = self.household_size_dist()
            house = nx.complete_graph(size)
            nx.relabel_nodes(house, lambda l: n + l, copy=False)

            self.g.add_nodes_from(house.nodes, household=household_id,
                                  household_size=size)

            self.g.add_edges_from(house.edges, household=household_id,
                                  household_size=size)

            households.append(house)

            n += size
            household_id += 1

        return households

    def _create_stubs(self, households: HOUSEHOLDS) -> STUBS:
        contacts = []
        for house in households:
            size = house.order()
            n_contacts = self.num_contact_dist(size)
            contacts.append(n_contacts)

        stubs = []

        for i in range(len(households)):

            house = households[i]

            nodes = list(house.nodes())[:contacts[i]]

            for node in nodes:
                num_copies = self.num_outside_edge_dist()
                stubs.extend([node] * num_copies)

        if len(stubs) % 2 > 0:
            unique_stubs = list(set(stubs))
            j = self._rng.integers(len(unique_stubs))
            stubs.append(unique_stubs[j])

        self._rng.shuffle(stubs)

        return stubs

    def _break_up_pairs(self, stubs: STUBS) -> STUBS:
        swaps = 1

        while swaps != 0:
            swaps = 0
            for i in range(0, len(stubs), 2):
                if self.g.nodes[stubs[i]]['household'] == \
                        self.g.nodes[stubs[i + 1]]['household']:
                    j = self._rng.integers(len(stubs))
                    stubs[i + 1], stubs[j] = stubs[j], stubs[i + 1]

                    swaps += 1

        return stubs

    def _connect_stubs(self, stubs: STUBS) -> None:
        """
        Part of the creation process to connect the stubs.
        :param stubs: List of stubs
        """

        # connect pairs of stubs
        for i in range(0, len(stubs), 2):
            # label inter-household edges as household 0 of size 0
            self.g.add_edge(stubs[i], stubs[i + 1], household=0,
                            household_size=0)


class DNGenerator(NetworkGenerator):
    """
    NetworkGenerator for a distanced network.
    """
    N: Final[str] = 'DN.n'
    HOUSEHOLD_SIZE_DIST: Final[str] = 'DN.household_size_dist'
    NUM_CONTACT_DIST: Final[str] = 'DN.num_contact_dist'
    NUM_OUTSIDE_EDGE_DIST: Final[str] = 'DN.num_outside_edge_dist'

    def __init__(self, params=None, limit=None, **kwargs):
        """
        Create a DNGenerator
        :param params: (optional) experiment parameters
        :param limit: (optional) maximum number of instances to generate
        :param kwargs: (optional) key word arguments. Can include:
            - `household_size_dist`
            - `num_contact_dist`
            - `num_outside_edge_dist`
            which otherwise have to be included in the `params` when generating
            the network. =
        """
        super(DNGenerator, self).__init__(params, limit)

        self._household_size_dist = kwargs.get('household_size_dist')
        self._num_contact_dist = kwargs.get('num_contact_dist')
        self._num_outside_edge_dist = kwargs.get('num_outside_edge_dist')

    def topology(self) -> str:
        """
        Return a flag to identify the topology.
        :return: topology flag
        """
        return 'DN'

    def _generate(self, params: Dict[str, Any]) -> nx.Graph:

        # Set the distribution functions (could also have been set at
        #  initialisation).
        self._household_size_dist = params.get(self.HOUSEHOLD_SIZE_DIST) \
                                    or self._household_size_dist
        assert self._household_size_dist is not None

        self._num_contact_dist = params.get(self.NUM_CONTACT_DIST) \
                                 or self._num_contact_dist
        assert self._num_contact_dist is not None

        self._num_outside_edge_dist = params.get(self.NUM_OUTSIDE_EDGE_DIST) \
                                      or self._num_outside_edge_dist
        assert self._num_outside_edge_dist is not None

        N = params[self.N]

        network = DistancedNetwork(
            N,
            self._household_size_dist,
            self._num_contact_dist,
            self._num_outside_edge_dist
        )

        network.create()

        return network.g
