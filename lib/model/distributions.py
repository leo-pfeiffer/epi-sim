import numpy as np
from typing import Optional, Callable

from lib.model.utils import binary_search_lowest_idx
from lib.model.network.network_data import NetworkData
from lib.model.types import RANDOM_SEED
from mpmath import polylog, mpf


class PowerLawCutoffDist:
    """
    Represent a power law cutoff distribution with a probability distribution
    function, mean, variance, and parameters tau and kappa.
    """

    def __init__(self, tau: float, kappa: int):
        """
        Create a PowerLawCutoffDist instance with parameters tau and kappa.
        :param tau: Exponent.
        :param kappa: Cutoff.
        """
        self._tau = tau
        self._kappa = kappa

    @property
    def tau(self):
        """
        Exponent value.
        :return: tau.
        """
        return self._tau

    @property
    def kappa(self):
        """
        Cutoff value.
        :return: kappa.
        """
        return self._kappa

    @property
    def p(self) -> Callable[[int], mpf]:
        """
        Probability distribution function of the power law with cutoff distribution. The distribution
        is discrete and only defined for whole numbers greater or equal one.
        :return: Probability distribution function.
        """

        # calculate normalisation constant
        C = 1 / polylog(self._tau, np.exp(-1. / self._kappa))

        # define the probability distribution function
        def p(k):
            # convert to float since np.power requires float
            k = float(k) if not isinstance(k, float) else k
            assert not k % 1
            assert k > 0
            return C * np.power(k, -self._tau) * np.exp(-k / self._kappa)

        # return the callable
        return p

    @property
    def mean(self) -> mpf:
        """
        Mean of the distribution.
        :return: mean.
        """
        # todo use epydemic gf
        n = polylog(self._tau - 1, np.exp(-1 / self._kappa))
        m = polylog(self._tau, np.exp(-1 / self._kappa))
        return n / m

    @property
    def var(self) -> mpf:
        """
        Variance of the distribution.
        :return: variance.
        """
        # todo use epydemic gf
        x = np.exp(-1 / self._kappa)
        n = polylog(self._tau - 2, x) - polylog(self._tau - 1, x)
        m = polylog(self._tau, x)
        g = n / m

        return g + self.mean - self.mean * self.mean


def discrete_trunc_normal(mu: float, std: Optional[float] = None,
                          seed: Optional[RANDOM_SEED] = None) -> int:
    """
    Draw an integer from a discrete normal distribution truncated in the
    range [1; infinity).
    :param mu: Mean of the distribution.
    :param std: Standard deviation of the distribution; defaults to mu / 2.
    :param seed: (optional) Random seed.
    :returns: Random integer.
    """
    rng = np.random.default_rng(seed=seed)
    std = mu / 2 if std is None else std
    return max(int(rng.normal(mu, std)), 1)


def discrete_trunc_exponential(exponent: float,
                               seed: Optional[RANDOM_SEED] = None) -> int:
    """
    Draw an integer from a discrete exponential distribution truncated in the
    range [1, infinity).
    :param exponent: Exponent of the exponential distribution.
    :param seed: (optional) Random seed.
    :returns: Random integer.
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


def num_contact_dist(size: int, std: float = 1,
                     seed: Optional[RANDOM_SEED] = None) -> int:
    """
    Draw random number of contacts within a household.
    :param size: households size
    :param std: standard deviation. defaults to 1.
    :param seed: random seed
    :return: number of intra household contact
    """
    mu = min(size / 2, 2)
    return discrete_trunc_normal(mu, std, seed=seed)
