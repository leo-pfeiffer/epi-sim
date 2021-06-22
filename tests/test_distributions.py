import pytest
from model.distributions import household_size_dist, node_degree_dist, draw_cbg
from tests.factory import *
import numpy as np

BASELINE = 3
SEED = np.random.default_rng(1)
PRE = create_network_data()
POST = create_network_data(True)

PRE.create_adjacency_list()
PRE.create_cum_prob()

POST.create_adjacency_list()
POST.create_cum_prob()

POST.calc_trip_count_change(PRE)
_TRIP_COUNT_CHANGE = POST.trip_count_change


def test_household_size_dist():

    mu_should = PRE.demographics['cbg1']['household_size']
    sigma_should = mu_should / 2

    nums = []
    for _ in range(10000):
        r = household_size_dist(mu=mu_should, seed=SEED)
        assert r >= 1
        assert r % 1 == 0
        nums.append(r)

    # margin of error is needed since it's a truncated normal dist...
    assert abs(np.mean(nums) - mu_should) < 0.5
    assert abs(np.std(nums) - sigma_should) < 0.25


def test_node_degree_dist():

    # No multiplier
    nums = []
    for _ in range(10000):
        r = node_degree_dist(BASELINE, SEED)
        assert r >= 1
        assert r % 1 == 0
        nums.append(r)

    assert abs(np.mean(nums) - BASELINE) < 0.5
    assert abs(np.std(nums) - BASELINE) < 0.5

    # With multiplier
    nums = []
    for _ in range(10000):
        exponent = BASELINE * _TRIP_COUNT_CHANGE['cbg1']
        r = node_degree_dist(exponent, SEED)
        assert r >= 1
        assert r % 1 == 0
        nums.append(r)

    m = _TRIP_COUNT_CHANGE['cbg1']
    assert abs(np.mean(nums) - BASELINE * m) < 0.5
    assert abs(np.std(nums) - BASELINE * m) < 0.5


def test_draw_cbg():

    n = 10000

    results = []
    for i in range(n):
        r = draw_cbg(PRE, 'cbg1', SEED)
        assert r in PRE.ordered_cbgs
        results.append(r)

    cbg_count = {}
    for res in results:
        if res in cbg_count:
            cbg_count[res] += 1
        else:
            cbg_count[res] = 1

    for cbg, ct in cbg_count.items():
        cbg_idx = PRE.ordered_cbgs.index(cbg)

        prop_is = ct / n
        prop_should = PRE.adjacency_list['cbg1'][cbg_idx]

        assert pytest.approx(prop_is, 0.1) == prop_should
