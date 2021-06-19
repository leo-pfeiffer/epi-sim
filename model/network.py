import numpy as np
import networkx as nx
from typing import Dict

from model.network_data import NetworkData
from model.distributions import household_size, household_contact, draw_cbg


class Network:
    def __init__(self, network_data, trip_count_change, N=10000,
                 baseline=3, multiplier=False, seed=None):
        self.network_data: NetworkData = network_data
        self.trip_count_change: Dict[str, float] = trip_count_change
        self.N: int = N
        self.baseline: float = baseline
        self.multiplier: bool = multiplier

        self._rng = np.random.default_rng(seed=seed)
        self._g: nx.Graph = nx.Graph()

    @property
    def g(self):
        return self._g

    def create(self):

        households, cbg_degree_map = self._create_households()
        stubs, cbg_degree_map = self._create_stubs(households, cbg_degree_map)
        stubs = self._create_stub_pairs(stubs, cbg_degree_map)
        self._break_up_pairs(stubs)

    def _create_households(self):

        household_id = 1
        households = []

        cbg_degree_map = {}
        total_node_ct = 0

        # add the nodes and create the household connections
        for cbg, demographic in self.network_data.demographics.items():

            # target number of nodes for current CBG
            N_cbg = int(demographic['population_prop'] * self.N)

            # current number of nodes of this CBG
            n = 0

            # initialise for later
            cbg_degree_map[cbg] = []

            # add households
            while n < N_cbg:
                # create household network
                size = household_size(self.network_data, cbg, seed=self._rng)
                house_net = nx.complete_graph(size)

                # add unique labels
                nx.relabel_nodes(house_net, lambda l: total_node_ct + l,
                                 copy=False)

                # add nodes and edges of the household to the main network
                self.g.add_nodes_from(house_net.nodes, household=household_id,
                                      household_size=size, cbg=cbg)

                self.g.add_edges_from(house_net.edges, household=household_id,
                                      household_size=size, cbg=cbg)

                households.append(house_net)

                # update iteration values
                n += size
                household_id += 1
                total_node_ct += size

        return households, cbg_degree_map

    def _create_stubs(self, households, cbg_degree_map):

        # create stubs for connections to outside of household
        stubs = []
        for i in range(len(households)):

            nodes = list(households[i].nodes)

            # if len(nodes) > 0:
            cbg = self.g.nodes[nodes[0]]['cbg']

            for node in nodes:
                # draw random degree
                degree = household_contact(self.trip_count_change,
                                           self.baseline, cbg,
                                           self.multiplier, seed=self._rng)

                # append `degree` number of copies of the current node
                new_stubs = [node] * degree
                stubs.extend(new_stubs)
                cbg_degree_map[cbg].extend(new_stubs)

        # add one more if number of stubs is odd
        if len(stubs) % 2:
            unique_stubs = list(set(stubs))
            j = self._rng.integers(len(unique_stubs))

            stubs.append(unique_stubs[j])
            cbg_degree_map[self.g.nodes[unique_stubs[j]]['cbg']] \
                .append(unique_stubs[j])

        return stubs, cbg_degree_map

    def _create_stub_pairs(self, stubs, cbg_degree_map):

        for i in range(0, len(stubs), 2):

            print(f"Creating stub pairs: {i} of {len(stubs)}", end="\r")

            while True:

                # draw a CBG from the rewire distribution
                cbg = self.g.nodes[stubs[i]]['cbg']
                target_cbg = draw_cbg(self.network_data, cbg, seed=self._rng)

                # make sure the drawn CBG has any available stubs at all
                if len(cbg_degree_map[target_cbg]) == 0:
                    continue

                # draw random stub from required CBG (preserving degree dist.)
                target_node = self._rng.choice(cbg_degree_map[target_cbg])
                j = stubs.index(target_node)

                # swap nodes
                stubs[i + 1], stubs[j] = stubs[j], stubs[i + 1]
                break

        return stubs

    def _break_up_pairs(self, stubs):
        swaps = 1
        while swaps != 0:

            print("Breaking up pairs...", end="\n")

            # iterate by two successive stubs at a time
            swaps = 0
            for i in range(0, len(stubs), 2):

                # break up if successive stubs are of same household
                if self.g.nodes[stubs[i]]['household'] == \
                        self.g.nodes[stubs[i + 1]]['household']:
                    # swap with random other stub
                    j = self._rng.integers(len(stubs))
                    stubs[i + 1], stubs[j] = stubs[j], stubs[i + 1]

                    swaps += 1

        # connect pairs of stubs
        for i in range(0, len(stubs), 2):
            # label inter-household edges as household 0 of size 0
            self.g.add_edge(stubs[i], stubs[i + 1], household=0,
                            household_size=0)
