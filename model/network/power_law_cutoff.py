# Human Contact Network
from typing import Dict, Any, Final, Callable

import networkx
from epydemic.generator import NetworkGenerator
from networkx import Graph
from mpmath import polylog, mpf
import numpy as np

from model.utils import discrete_rejection_sample


class PowerLawCutoffNetwork(NetworkGenerator):
    """
    Generate a network with node degrees following a power law distribution with cutoff as described by
        Newman, M. E., Watts, D. J., and Strogatz, S. H. (2002). Random graph models of social networks.
        Proceedings of the national academy of sciences, 99(suppl 1):2566–2572.
    The exponent of the power law distribution is given by the `TAU` and the cutoff value for degrees is `KAPPA`.
    The network has `N` nodes.

    :param params: (optional) experiment parameters
    :param limit: (optional) maximum number of instances to generate
    """

    N: Final[str] = 'PLC.n'
    TAU: Final[str] = 'PLC.tau'
    KAPPA: Final[str] = 'PLC.kappa'

    def __init__(self, params=None, limit=None):
        super(PowerLawCutoffNetwork, self).__init__(params, limit)

    def topology(self) -> str:
        """
        Return a flag to identify the topology
        :return: topology flag
        """
        return 'PLC'

    def _generate(self, params: Dict[str, Any]) -> Graph:
        """
        Generate a graph with node degrees following a power law distribution with cutoff.
        :param params: experiment parameters
        :return: Graph
        """
        n = params[self.N]
        tau = params[self.TAU]
        kappa = params[self.KAPPA]

        # get the distribution function
        p = self.distribution(tau, kappa)

        # generate and return graph
        return self._generate_with_degree_distribution(p=p, n=n, max_deg=kappa)

    @staticmethod
    def _generate_with_degree_distribution(p, n, max_deg) -> Graph:
        """
        Generate random graph with a specified degree distribution.
        :param p: Probability distribution function.
        :param n: Number of nodes in the graph.
        :param max_deg: Maximum degree of the nodes.
        :return: Network
        """

        # initialise values
        rng = np.random.default_rng()
        nodes = []
        degree_sum = 0

        # create list of random node degrees
        for i in range(n):
            k = discrete_rejection_sample(p=p, a=1, b=max_deg, seed=rng)
            nodes.append(k)
            degree_sum += k

        # keep randomly randomly replacing until degree sum is even
        while degree_sum % 2:

            # delete old node
            i = rng.integers(0, len(nodes) - 1)
            degree_sum -= nodes[i]
            del nodes[i]

            # add new node
            k = discrete_rejection_sample(p=p, a=1, b=max_deg, seed=rng)
            nodes.append(k)
            degree_sum += k

        # create and return the graph
        return networkx.configuration_model(nodes, create_using=Graph())

    @staticmethod
    def distribution(tau: float, kappa: int) -> Callable[[int], mpf]:
        """
        Probability distribution function of the power law with cutoff distribution. The distribution
        is discrete and only defined for whole numbers greater or equal one.
        :param tau: exponent of the power law distribution.
        :param kappa: cutoff value.
        :return: Value from the probability distribution function.
        """

        # calculate normalisation constant
        C = 1 / polylog(tau, np.exp(-1. / kappa))

        # todo potentially allow k to be an array:
        #   Would only have to change assertions.
        #   Might be helpful if I find a way to speed up the random generator.
        # define the probability distribution function
        def p(k):
            assert not k % 1
            assert k > 0
            return C * np.power(k, -tau) * np.exp(-k / kappa)

        # return the callable
        return p
