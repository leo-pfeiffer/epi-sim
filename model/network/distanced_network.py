from typing import Callable, Optional, List

import networkx as nx
import numpy as np

from model.types import RANDOM_SEED

# special types for convenience...
HOUSEHOLDS = List[nx.Graph]
STUBS = List[int]


# todo comments, docstrings, ...

class DistancedNetwork:
    """
    Implementation of the distanced network presented in
        Dobson 2020 - Epidemic Modelling, pp. 157
    """

    def __int__(self, N: int,
                cluster_size_dist: Callable, contact_dist: Callable,
                cluster_contact_dist: Callable, seed: Optional[RANDOM_SEED]):
        self.N = N
        self.cluster_size_dist = cluster_size_dist
        self.contact_dist = contact_dist
        self.cluster_contact_dist = cluster_contact_dist

        self._rng = np.random.default_rng(seed=seed)
        self._g: nx.Graph = nx.Graph()

    @property
    def g(self):
        return self._g

    def create(self):
        households = self._households()
        stubs = self._create_stubs(households)
        stubs = self._break_up_pairs(stubs)
        self._connect_stubs(stubs)

    def _create_households(self) -> HOUSEHOLDS:
        household_id = 1
        households = []
        n = 0

        while n < self.N:
            size = self.cluster_size_dist()
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
            degree = self.contact_dist(size)
            contacts.append(degree)

        stubs = []

        for i in range(len(households)):

            house = households[i]

            nodes = list(house.nodes())[:contacts[i]]

            for node in nodes:
                num_copies = self.cluster_contact_dist()
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
