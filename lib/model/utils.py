# Model utils
from typing import Callable, Union, Optional
import numpy as np

from lib.model.types import RANDOM_SEED


def discrete_rejection_sample(p: Callable[[int], Union[float, int]], a: int,
                              b: int, seed: Optional[RANDOM_SEED] = None) -> int:
    """
    Perform rejection sampling for a using the provided discrete probability
    distribution function `p`.
    :param p: Probability distribution function.
    :param a: Lower bound of the sample values.
    :param b: Upper bound of the sample values.
    :param seed: Random seed.
    :return: Sampled integer.
    """
    rng = np.random.default_rng(seed=seed)

    while True:
        # draw a random integer from the specified range
        x = rng.integers(a, b)

        # accept x with probability p(x) else reject x
        if rng.random() < p(x):
            return x


def binary_search_lowest_idx(arr, left, right, x) -> int:
    """
    Generic binary search function that finds an element in an array. If the
    element is not unique in the array, the element with the lowest index is
    returned.
    :param arr: Array like object.
    :param left: Most left index to start the search.
    :param right: Most right index to start the search.
    :param x: The element to search for.
    :returns: Index of the most left element found found.
    """

    while left < right:
        mid = (left + right) // 2
        if arr[mid] < x:
            left = mid + 1
        else:
            right = mid
    return left
