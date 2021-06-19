import numpy as np
from typing import Union

from model.utils import binary_search
from model.network import NetworkData


def household_size(network_data: NetworkData,
                   cbg: str,
                   seed: Union[int, np.random.Generator, None] = None) -> int:
    """
    Household size distribution is drawn from normal distribution with mean
    according to mean household size of CBG.
    :param network_data:
    :param seed: random seed.
    :param cbg: CBG of the household.
    :returns: Household size.
    """
    rng = np.random.default_rng(seed=seed)
    mu = network_data.demographics[cbg]['household_size']
    sd = mu / 2
    return max(int(rng.normal(mu, sd)), 1)


# todo type hint
def household_contact(trip_count_change, baseline: float, cbg: str,
                      multiplier: bool,
                      seed: Union[int, np.random.Generator, None] = None) -> int:
    """
    Number of connections from a node to another node outside the household.
    :param trip_count_change:
    :param seed: random seed.
    :param baseline: baseline value for the exponent of the degree distribution.
    :param cbg: CBG of the current household.
    :param multiplier: reduce exponent by factor.
    :returns: Number of connections to outside the household.
    """
    rng = np.random.default_rng(seed=seed)
    if multiplier:
        exponent = baseline * trip_count_change[cbg]
    else:
        exponent = baseline
    return max(int(rng.exponential(exponent)), 1)


def draw_cbg(network_data: NetworkData, cbg: str,
             seed: Union[int, np.random.Generator, None] = None) -> str:
    """
    For a given CBG draw from the corresponding rewire distribution and return
    a random CBG to rewire to.
    :param network_data:
    :param seed: random seed.
    :param cbg: CBG to be rewired.
    """
    rng = np.random.default_rng(seed=seed)
    r = rng.random()

    # return index where p >= r for the first time
    arr = network_data.cum_prob[cbg]
    idx = binary_search(arr, 0, len(arr) - 1, r)
    return network_data.ordered_cbgs[idx]
