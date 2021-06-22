import pytest
from tests.factory import *


def test_create_network_data_instance():
    demographics = create_demographics()
    comb_counts, trip_counts = create_counts()
    network_data = NetworkData(demographics, comb_counts, trip_counts)
    assert isinstance(network_data, NetworkData)


def test_create_adjacency_list():
    network_data = create_network_data()
    network_data.create_adjacency_list()

    ordered_cbgs = network_data.ordered_cbgs
    adj_list = network_data.adjacency_list
    assert pytest.approx(sum(adj_list[ordered_cbgs[0]]), 0.001) == 1


def test_create_cum_prob():
    network_data = create_network_data()
    network_data.create_adjacency_list()
    network_data.create_cum_prob()

    ordered_cbgs = network_data.ordered_cbgs
    cum_prob = network_data.cum_prob

    assert pytest.approx(cum_prob[ordered_cbgs[0]][-1], 0.001) == 1


def test_create_cum_prob_requires_adjacency_list():
    network_data = create_network_data()

    with pytest.raises(AttributeError):
        network_data.create_cum_prob()


def test_calc_trip_count_change():
    pre = create_network_data()
    post = create_network_data(True)

    post.calc_trip_count_change(pre)
    trip_count_change = post.trip_count_change

    for k, v in trip_count_change.items():
        assert pytest.approx(v, 0.1) == 0.5
