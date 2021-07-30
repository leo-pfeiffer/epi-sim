# Unit tests for model utils
from lib.model.utils import discrete_rejection_sample, binary_search_lowest_idx
import numpy as np


def test_discrete_rejection_sample_expected():
    # probability distribution, 1 if x is 1 else 0
    # must always return 1
    assert discrete_rejection_sample(lambda x: int(x == 1), 0, 2, seed=0) == 1


def test_discrete_rejection_sample_range():

    # test a few times to make sure ...
    for i in range(1000):
        x = discrete_rejection_sample(lambda y: 0.5, 0, 5, seed=0)
        assert 0 <= x < 10


def test_binary_search():
    ls = np.array([0.2, 0.2, 0.2, 0.2, 0.2]).cumsum()
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 0.1) == 0
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 0.2) == 0
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 0.3) == 1
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 0.9) == 4
    assert binary_search_lowest_idx(ls, 0, len(ls) - 1, 1) == 4
