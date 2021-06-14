# Human Contact Network
from typing import Dict, Any, Final, Callable, Union

import networkx
from epydemic.generator import NetworkGenerator
from networkx import Graph
from mpmath import polylog
import numpy as np


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

    N: Final[str] = 'PLC.N'
    TAU: Final[str] = 'PLC.tau'
    KAPPA: Final[str] = 'PLC.kappa'

    def __init__(self, params=None, limit=None):
        super(PowerLawCutoffNetwork, self).__init__(params, limit)

    def topology(self) -> str:
        """
        Return a flag to identify the topology
        :return: topology flag
        """
        pass

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

        rng = np.random.default_rng()
        nodes = []
        degree_sum = 0

        # create list of random node degrees
        for i in range(n):
            k = self.discrete_rejection_sample(p=p, a=1, b=kappa, rng=rng)
            nodes.append(k)
            degree_sum += k

        # keep randomly randomly replacing until degree sum is even
        while degree_sum % 2:
            i = rng.integers(0, len(nodes) - 1)
            degree_sum -= nodes[i]
            del nodes[i]

            k = self.discrete_rejection_sample(p=p, a=1, b=kappa, rng=rng)
            nodes.append(k)
            degree_sum += k

        # create and return the graph
        return networkx.configuration_model(nodes, create_using=Graph())

    @staticmethod
    def discrete_rejection_sample(p: Callable[[int], Union[float, int]], a: int, b: int,
                                  rng=np.random.default_rng()):
        """
        Perform rejection sampling for a using the provided discrete probability distribution function `p`.
        :param p: Probability distribution function
        :param a: Lower bound of the sample values
        :param b: Upper bound of the sample values
        :param rng: Numpy random generator: Todo type hint
        :return: Sampled value
        """
        while True:
            # draw a random integer from the specified range
            x = rng.integers(a, b)

            # accept x with probability p(x) else reject x
            if rng.random() < p(x):
                return x

    @staticmethod
    def distribution(tau: float, kappa: int) -> Callable[[int], float]:
        """
        Probability distribution function of the power law with cutoff distribution.
        # todo describe that this is technically continuous but type hints suggest discrete since that's how we use it
        :param tau: exponent of the power law distribution
        :param kappa: cutoff value
        :return: Value from the probability distribution function
        """

        # calculate normalisation constant
        C = 1 / polylog(tau, np.exp(-1. / kappa))

        # return distribution function
        return lambda k: float(C * np.power(k, -tau) * np.exp(-k / kappa))
