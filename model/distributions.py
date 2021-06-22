import numpy as np
from typing import Union

from model.utils import binary_search_lowest_idx
from model.network.network_data import NetworkData
from model.types import RANDOM_SEED


def household_size_dist(mu: float, std: Union[float, None] = None,
                        seed: Union[RANDOM_SEED, None] = None) -> int:
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
                     seed: Union[RANDOM_SEED, None] = None) -> int:
    """
    Return node degree from a discrete exponential distribution.
    :param exponent: Exponent of the exponential distribution.
    :param seed: (optional) Random seed.
    :returns: Number of connections to outside the household.
    """
    rng = np.random.default_rng(seed=seed)
    return max(int(rng.exponential(exponent)), 1)


def draw_cbg(network_data: NetworkData, cbg: str,
             seed: Union[RANDOM_SEED, None] = None) -> str:
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
