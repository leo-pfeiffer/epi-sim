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


def binary_search(arr, left, right, x) -> int:
    """
    Generic binary search function that finds the element
    *furthest to the left* of an array.
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
