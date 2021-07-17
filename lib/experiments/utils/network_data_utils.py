# This file contains some utils to loading, creating and processing data
#  required for the creation of NetworkData instances used for mobility
#  networks.

from typing import Dict

from lib.configuration import OUT
from lib.experiments.utils.data_repo_api import DataRepoAPI
from lib.experiments.utils.file_utils import load_pickle_from_disk
from lib.model.network.network_data import NetworkData


def load_network_data_from_files(names: Dict[str, str],
                                 dirname: str = OUT,
                                 disk: bool = False) -> Dict[str, NetworkData]:
    """
    Utility function to create the pre and post network data from input files.
    By default data is pulled from data repository unless `disk=True`.
    :param names: file names of input data
    :param dirname: (optional) directory of the files
    :param disk: (optional) load from disk
    :return: dictionary with network data
    """

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
    if disk:
        demographics = load_pickle_from_disk(dirname, names['demographics'])

        # Load comb counts
        comb_pre = load_pickle_from_disk(dirname, names['comb_pre'])
        comb_post = load_pickle_from_disk(dirname, names['comb_post'])

        # Load trip counts
        trip_pre = load_pickle_from_disk(dirname, names['trip_pre'])
        trip_post = load_pickle_from_disk(dirname, names['trip_post'])

    else:
        demographics = DataRepoAPI.get_pickle_file(names['demographics'])
        comb_pre = DataRepoAPI.get_pickle_file(names['comb_pre'])
        comb_post = DataRepoAPI.get_pickle_file(names['comb_post'])
        trip_pre = DataRepoAPI.get_pickle_file(names['trip_pre'])
        trip_post = DataRepoAPI.get_pickle_file(names['trip_post'])

    # return the instances
    return make_network_data(demographics, comb_pre, comb_post, trip_pre,
                             trip_post)


def make_network_data(demographics, comb_pre, comb_post, trip_pre, trip_post):
    """
    Return a Pre and Post NetworkData instance from the input files.
    :param demographics: Demographics data.
    :param comb_pre: CBG trip combinations (pre)
    :param comb_post: CBG trip combinations (post)
    :param trip_pre: CBG trip counts (pre)
    :param trip_post: CBG trip counts (post)
    :return: Pre and Post NetworkData instance
    """
    # create the instances
    network_data_pre = NetworkData(demographics, comb_pre, trip_pre)
    network_data_post = NetworkData(demographics, comb_post, trip_post)

    # perform required calculations
    network_data_post.calc_trip_count_change(network_data_pre)

    network_data_pre.create_adjacency_list()
    network_data_post.create_adjacency_list()

    network_data_pre.create_cum_prob()
    network_data_post.create_cum_prob()

    return dict(pre=network_data_pre, post=network_data_post)
