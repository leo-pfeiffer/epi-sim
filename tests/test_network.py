# Unit tests for network generators
import pytest


def test_plc_generate(plc):
    """
    Test we can generate the network
    """
    _ = plc.generate()


def test_plc_topology(plc):
    """
    Test we get the right topology name for the PLC network.
    """
    assert plc.topology() == 'PLC'


def test_plc_distribution_smaller_one(plc_distribution):
    """
    Test the PLC distribution returns only probabilities between 0 and 1.
    """
    for x in range(1, 11):
        assert 0 < plc_distribution(x) < 1


def test_plc_distribution_sum_to_one(plc_distribution):
    """
    Test the PLC distribution returns values that sum to 1.
    """
    vals = []
    for x in range(1, 100):
        vals.append(plc_distribution(x))
    assert pytest.approx(sum(vals), abs=1e-3) == 1


def test_plc_distribution_assertions(plc_distribution):
    """
    Test the PLC distribution raises Errors when passing invalid values.
    """
    # must be whole number
    with pytest.raises(AssertionError) as err:
        plc_distribution(k=1.5)  # noqa

    # must be greater than one
    with pytest.raises(AssertionError) as err:
        plc_distribution(k=0)  # noqa
