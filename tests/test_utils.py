# Unit tests for model utils
from model.utils import discrete_rejection_sample, binary_search_lowest_idx
import numpy as np


def test_discrete_rejection_sample_expected():
    # probability distribution, 1 if x is 1 else 0
    p = lambda x: int(x == 1)

    # must always return 1
    assert discrete_rejection_sample(p, 0, 2) == 1


def test_discrete_rejection_sample_range():
    p = lambda x: 0.5

    # test a few times to make sure ...
    for i in range(1000):
        x = discrete_rejection_sample(p, 0, 5)
        assert 0 <= x < 10


def test_binary_search():
    ls = np.array([0.2, 0.2, 0.2, 0.2, 0.2]).cumsum()
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 0.1) == 0
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 0.2) == 0
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 0.3) == 1
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 0.9) == 4
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 1) == 4
