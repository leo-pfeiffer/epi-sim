import numpy as np
import networkx as nx
from typing import Dict, Union, List, Tuple, Any, Final, Callable
from epydemic import NetworkGenerator
from networkx import Graph, read_graphml

from model.network.network_data import NetworkData
from model.distributions import household_size_dist, draw_cbg, PowerLawCutoffDist
from model.types import RANDOM_SEED

# special types for convenience...
from model.utils import discrete_rejection_sample

HOUSEHOLDS = List[nx.Graph]
STUBS = List[int]
CBG_DEGREE_MAP = Dict[str, List[int]]


class MobilityNetwork:
    """
    Mobility Network created from mobility data.
    :param network_data: NetworkData containing mobility data from which to
        create the network.
    :param N: Number of nodes (approximate) in the network.
    :param baseline: Baseline value for the exponent of the exponential
        distribution used for the node degrees.
    :param multiplier: (optional) True the trip_count_change multiplier should
        be applied to the exponent of the exponential distribution for the
        node degrees.
    :param seed: (optional) Random seed for reproducibility.
    """

    def __init__(self, network_data: NetworkData,
                 degree_dist: Callable,
                 N: int = 10000,
                 multiplier: bool = False,
                 max_deg: int = 100,
                 seed: Union[RANDOM_SEED, None] = None):

        self.network_data: NetworkData = network_data
        self.degree_dist: Callable[[int], float] = degree_dist
        self.N: int = N
        self.max_deg: int = max_deg
        self.multiplier: bool = multiplier

        if self.multiplier:
            try:
                assert hasattr(self.network_data, 'trip_count_change')
            except AssertionError as ae:
                raise ValueError('When multiplier=True, the trip_count_change '
                                 'attribute of the network_data object must '
                                 'be set. Hint: Run the calc_trip_count_change '
                                 'method on the network_data instance first.')

        self._rng = np.random.default_rng(seed=seed)
        self._g: nx.Graph = nx.Graph()

    @property
    def g(self):
        return self._g

    def create(self):
        """
        Create the network. This executes all steps of the creation process in
        order. The algorithm is adapted from
            Dobson (2020). Epidemic Modelling. (pp. 157)
        but adapted to base the network on mobility data.
        """

        households = self._create_households()
        stubs, cbg_degree_map = self._create_stubs(households)
        stubs = self._create_stub_pairs(stubs, cbg_degree_map)
        stubs = self._break_up_pairs(stubs)
        self._connect_stubs(stubs)

    def _create_households(self) -> HOUSEHOLDS:
        """
        Part of the creation process to built household clusters for each CBG.
        The number of nodes per CBG is proportional to the population of
        the CBG. The household size is drawn from a distribution parametrised
        with the (real world) mean household size.
        :return: List of household graphs.
        """

        household_id = 1
        households = []

        total_node_ct = 0

        # add the nodes and create the household connections
        for cbg, demographic in self.network_data.demographics.items():

            # target number of nodes for current CBG
            N_cbg = int(demographic['population_prop'] * self.N)

            # current number of nodes of this CBG
            n = 0

            # add households
            while n < N_cbg:
                # create household network
                mu = self.network_data.demographics[cbg]['household_size']
                size = household_size_dist(mu=mu, seed=self._rng)
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

        return households

    def _create_stubs(self, households: HOUSEHOLDS) -> \
            Tuple[STUBS, CBG_DEGREE_MAP]:
        """
        Part of the creation process to create (still) unconnected nodes as
        extra-household connections.
        :param households: List of household graphs.
        :return: List of stubs containing copies of existing nodes; A map
            with the stubs per CBG.
        """

        cbg_degree_map = {k: [] for k in self.network_data.demographics.keys()}

        # create stubs for connections to outside of household
        stubs = []
        for i in range(len(households)):

            nodes = list(households[i].nodes)

            cbg = self.g.nodes[nodes[0]]['cbg']

            for node in nodes:
                # draw random degree
                degree = discrete_rejection_sample(p=self.degree_dist,
                                                   a=1, b=self.max_deg,
                                                   seed=self._rng)

                if self.multiplier:
                    m = self.network_data.trip_count_change[cbg]
                    degree = max(int(m * degree), 1)

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

    def _create_stub_pairs(self, stubs: STUBS,
                           cbg_degree_map: CBG_DEGREE_MAP):
        """
        Part of the creation process to pair the stubs in a way that favours
        connections between CBGs that are favoured in the mobility data too.
        :param stubs: List of stubs.
        :param cbg_degree_map: Map of stub nodes to CBG
        """

        # todo for validation, compare adjacency list of graph to empirical
        #  adjacency list

        for i in range(0, len(stubs), 2):

            while True:

                # draw a CBG from the CBG connection distribution
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

    def _break_up_pairs(self, stubs: STUBS) -> STUBS:
        """
        Part of the creation process to break up any intra-household stub pairs
        since stubs are supposed to connect between households.
        :param stubs: List of stubs.
        """
        swaps = 1
        while swaps != 0:

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

        return stubs

    def _connect_stubs(self, stubs: STUBS) -> None:
        """
        Part of the creation process to connect the stubs.
        :param stubs: List of stubs.
        """

        # connect pairs of stubs
        for i in range(0, len(stubs), 2):
            # label inter-household edges as household 0 of size 0
            self.g.add_edge(stubs[i], stubs[i + 1], household=0,
                            household_size=0)


class MNGenerator(NetworkGenerator):
    """
    Abstract NetworkGenerator for MobilityNetworks. Defines the `topology`
    method for all subclasses.
    Sub-classes must still overwrite the `_generate` method.

    :param params: (optional) experiment parameters
    :param limit: (optional) maximum number of instances to generate
    """

    N: Final[str] = 'MN.n'
    EXPONENT: Final[str] = 'MN.exponent'
    CUTOFF: Final[str] = 'MN.cutoff'

    def __init__(self, params=None, limit=None):
        super(MNGenerator, self).__init__(params, limit)

    def topology(self) -> str:
        """
        Return a flag to identify the topology.
        :return: topology flag
        """
        return 'MN'

    def _generate(self, params: Dict[str, Any]) -> Graph:
        raise NotImplementedError('MNGenerator._generate needs to be '
                                  'overridden by sub-classes')


class MNGeneratorFromFile(MNGenerator):
    """
    NetworkGenerator to generate MobilityNetworks from GraphML file.

    :param params: (optional) experiment parameters
    :param limit: (optional) maximum number of instances to generate
    """

    PATH: Final[str] = 'MN.path'

    def __init__(self, params=None, limit=None):
        super(MNGeneratorFromFile, self).__init__(params, limit)

    def _generate(self, params: Dict[str, Any]) -> Graph:
        """
        Generate the graph of a mobility network from a GraphML file
        :param params: experiment parameters
        :return: Graph
        """
        g = read_graphml(params[self.PATH])
        return g


class MNGeneratorFromNetworkData(MNGenerator):
    """
    NetworkGenerator to generate MobilityNetworks from a NetworkData object.

    :param params: (optional) experiment parameters
    :param limit: (optional) maximum number of instances to generate
    """

    NETWORK_DATA: Final[str] = 'MN.network_data'
    MULTIPLIER: Final[str] = 'MN.multiplier'
    SEED: Final[str] = 'MN.seed'

    def __init__(self, params=None, limit=None):
        super(MNGeneratorFromNetworkData, self).__init__(params, limit)

    def _generate(self, params: Dict[str, Any]) -> nx.Graph:
        """
        Generate the graph of a mobility network from a NetworkData object.
        :param params: experiment parameters
        :return: Graph
        """

        network_data = params[self.NETWORK_DATA]
        n = params[self.N]
        multiplier = params[self.MULTIPLIER]

        exponent = params[self.EXPONENT]
        cutoff = params[self.CUTOFF]

        degree_dist = PowerLawCutoffDist(exponent, cutoff).p

        # optional args
        seed = params.get(self.SEED, None)

        mobility_network = MobilityNetwork(network_data=network_data,
                                           degree_dist=degree_dist,
                                           N=n,
                                           multiplier=multiplier,
                                           seed=seed)

        mobility_network.create()

        return mobility_network.g
