import os
import pickle
from configuration import OUT
from model.network.network_data import NetworkData


def load_network_data_from_files(names: dict[str, str],
                                 dirname: str = OUT) -> dict[str, NetworkData]:
    """
    Utility function to create the pre and post network data from input files.
    :param names: file names of input data
    :param dirname: directory of the files
    :return: dictionary with network data
    """

    # todo get from Github data repo

    # default file names
    if names is None:
        names = dict(
            demographics='demographics.pkl',
            comb_pre='comb_counts_pre.pkl',
            comb_post='comb_counts_post.pkl',
            trip_pre='trip_counts_pre.pkl',
            trip_post='trip_counts_post.pkl',
        )

    # Load demographics
    demographics = pickle.load(
        open(os.path.join(dirname, names['demographics']), 'rb')
    )

    # Load comb counts
    comb_counts_pre = pickle.load(
        open(os.path.join(dirname, names['comb_pre']), 'rb')
    )
    comb_counts_post = pickle.load(
        open(os.path.join(dirname, names['comb_post']), 'rb')
    )

    # Load trip counts
    trip_counts_pre = pickle.load(
        open(os.path.join(dirname, 'trip_counts_pre.pkl'), 'rb')
    )
    trip_counts_post = pickle.load(
        open(os.path.join(dirname, 'trip_counts_post.pkl'), 'rb')
    )

    # create the instances
    network_data_pre = NetworkData(
        demographics, comb_counts_pre, trip_counts_pre
    )
    network_data_post = NetworkData(
        demographics, comb_counts_post, trip_counts_post
    )

    # perform required calculations
    network_data_post.calc_trip_count_change(network_data_pre)

    network_data_pre.create_adjacency_list()
    network_data_post.create_adjacency_list()

    network_data_pre.create_cum_prob()
    network_data_post.create_cum_prob()

    return dict(
        pre=network_data_pre,
        post=network_data_post
    )
