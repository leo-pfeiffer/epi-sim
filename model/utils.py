# Model utils

from typing import Callable, Union
import numpy as np


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
