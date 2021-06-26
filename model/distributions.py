import numpy as np
from typing import Union, Optional, Callable

from model.utils import binary_search_lowest_idx
from model.network.network_data import NetworkData
from model.types import RANDOM_SEED
from mpmath import polylog, mpf


# todo make names a bit more generic
def power_law_cutoff_dist(tau: float, kappa: int) -> Callable[[int], mpf]:
    """
    Probability distribution function of the power law with cutoff distribution. The distribution
    is discrete and only defined for whole numbers greater or equal one.
    :param tau: exponent of the power law distribution.
    :param kappa: cutoff value.
    :return: Value from the probability distribution function.
    """

    # calculate normalisation constant
    C = 1 / polylog(tau, np.exp(-1. / kappa))

    # define the probability distribution function
    def p(k):
        # convert to float since np.power requires float
        k = float(k) if not isinstance(k, float) else k
        assert not k % 1
        assert k > 0
        return C * np.power(k, -tau) * np.exp(-k / kappa)

    # return the callable
    return p


def household_size_dist(mu: float, std: Union[float, None] = None,
                        seed: Optional[RANDOM_SEED] = None) -> int:
    """
    Return a random household size from (discrete) normal distribution.
    :param mu: Mean of the distribution.
    :param std: (optional) Standard deviation of the distribution. If not
        specified, std = mu / 2
    :param seed: (optional) Random seed.
    :returns: Household size.
    """
    rng = np.random.default_rng(seed=seed)
    std = mu / 2 if std is None else std
    return max(int(rng.normal(mu, std)), 1)


def node_degree_dist(exponent: float,
                     seed: Optional[RANDOM_SEED] = None) -> int:
    """
    Return node degree from a discrete exponential distribution.
    :param exponent: Exponent of the exponential distribution.
    :param seed: (optional) Random seed.
    :returns: Number of connections to outside the household.
    """
    rng = np.random.default_rng(seed=seed)
    return max(int(rng.exponential(exponent)), 1)


def draw_cbg(network_data: NetworkData, cbg: str,
             seed: Optional[RANDOM_SEED] = None) -> str:
    """
    Draw a random target CBG for a given CBG. The selection of the target CBG
    is based on the distribution of trips from the given CBG to all other CBGs.
    :param network_data: NetworkData
    :param cbg: Origin CBG.
    :param seed: (optional) Random seed.
    """
    rng = np.random.default_rng(seed=seed)
    r = rng.random()

    # return index where p >= r for the first time
    arr = network_data.cum_prob[cbg]
    idx = binary_search_lowest_idx(arr, 0, len(arr) - 1, r)
    return network_data.ordered_cbgs[idx]


def intra_household_contacts(size: int, std: float = 1,
                             seed: Optional[RANDOM_SEED] = None) -> int:
    """
    Draw random number of contacts within a household.
    :param size: households size
    :param std: standard deviation. defaults to 1.
    :param seed: random seed
    :return: number of intra household contact
    """
    rng = np.random.default_rng(seed=seed)
    return max(int(rng.normal(min(size / 2, 1), std)), 1)
