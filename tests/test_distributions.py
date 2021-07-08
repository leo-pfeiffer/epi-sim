import pytest
from model.distributions import discrete_trunc_normal, \
    discrete_trunc_exponential, draw_cbg, num_contact_dist, PowerLawCutoffDist
from tests.factory import *
import numpy as np
from mpmath import polylog

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

TAU = 0.2
KAPPA = 10
PLC_DIST = PowerLawCutoffDist(tau=TAU, kappa=KAPPA)
PLC = PLC_DIST.p


def test_discrete_trunc_normal():
    mu_should = PRE.demographics['cbg1']['household_size']
    sigma_should = mu_should / 2

    nums = []
    for _ in range(10000):
        r = discrete_trunc_normal(mu=mu_should, seed=SEED)
        assert r >= 1
        assert r % 1 == 0
        nums.append(r)

    # margin of error is needed since it's a truncated normal dist...
    assert abs(np.mean(nums) - mu_should) < 0.5
    assert abs(np.std(nums) - sigma_should) < 0.25


def test_num_contact_dist():
    size = 10
    std = 2
    mu_should = min(size / 2, 2)

    nums = []
    for _ in range(10000):
        r = num_contact_dist(size=size, std=std, seed=SEED)
        assert r >= 1
        assert r % 1 == 0
        nums.append(r)

    # margin of error is needed since it's a truncated normal dist...
    assert abs(np.mean(nums) - mu_should) < size / 10
    assert abs(np.std(nums) - std) < std / 2


def test_discrete_trunc_exponential():
    # No multiplier
    nums = []
    for _ in range(10000):
        r = discrete_trunc_exponential(BASELINE, SEED)
        assert r >= 1
        assert r % 1 == 0
        nums.append(r)

    assert abs(np.mean(nums) - BASELINE) < 0.5
    assert abs(np.std(nums) - BASELINE) < 0.5

    # With multiplier
    nums = []
    for _ in range(10000):
        exponent = BASELINE * _TRIP_COUNT_CHANGE['cbg1']
        r = discrete_trunc_exponential(exponent, SEED)
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


def test_plc_distribution_smaller_one():
    """
    Test the PLC distribution returns only probabilities between 0 and 1.
    """
    for x in range(1, 11):
        assert 0 < PLC(x) < 1


def test_plc_distribution_sum_to_one():
    """
    Test the PLC distribution returns values that sum to 1.
    """
    values = []
    for x in range(1, 100):
        values.append(PLC(x))
    assert pytest.approx(sum(values), abs=1e-3) == 1


def test_plc_distribution_assertions():
    """
    Test the PLC distribution raises Errors when passing invalid values.
    """
    # must be whole number
    with pytest.raises(AssertionError):
        PLC(1.5)  # noqa

    # must be greater than one
    with pytest.raises(AssertionError):
        PLC(0)  # noqa


def test_plc_mean():
    """
    Test PLC distribution returns correct mean.
    """
    n = polylog(TAU-1, np.exp(-1 / KAPPA))
    m = polylog(TAU, np.exp(-1 / KAPPA))

    assert PLC_DIST.mean == n / m


def test_plc_variance():
    """
    Test PLC distribution returns correct variance.
    """
    x = np.exp(-1 / KAPPA)
    n = polylog(TAU-1, x)
    m = polylog(TAU, x)

    g = (polylog(TAU-2, x) - polylog(TAU-1, x)) / polylog(TAU, x)

    assert PLC_DIST.var == g + (n/m) - (n/m) * (n/m)
