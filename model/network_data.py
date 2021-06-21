from __future__ import annotations

import numpy as np
from typing import Dict, List, Tuple

from dataclasses import dataclass, field

from model.types import TRIP_COUNT_CHANGE


@dataclass
class NetworkData:
    demographics: Dict
    comb_counts: Dict[Tuple[str, str], int]
    trip_counts: Dict[str, int]

    # not initialised
    ordered_cbgs: List[str] = field(init=False)
    adjacency_list: Dict[str, List[float]] = field(init=False)
    cum_prob: Dict[str, np.array] = field(init=False)

    def __post_init__(self):
        self.ordered_cbgs = sorted(self.demographics.keys())

    def create_adjacency_list(self) -> None:
        """
        Create an adjacency list in the form of a dictionary.
        The keys are the CGBs and the values are ordered lists of transition
        probabilities to other CBGs.
        The probabilities are in the same order as `ordered_cbgs`.
        The transition probability from CBG i to CBG j is
        P(i, j) = count(trips between i and j) / count(all trips from i to a CBG).
        :param comb_counts: Total count of all trips between two CGBs.
        :param trip_counts: Total count of all trips from each CGB.
        :returns: Adjacency list with probabilites.
        """

        self.adjacency_list: Dict[str, List[float]] = {}

        for i in self.ordered_cbgs:
            self.adjacency_list[i] = []
            for j in self.ordered_cbgs:
                # count of trips between
                comb = (i, j)
                trips_between = 0 if comb not in self.comb_counts else \
                    self.comb_counts[comb]

                # ratio of all trips from i
                p = 0 if i not in self.trip_counts else \
                    trips_between / self.trip_counts[i]

                self.adjacency_list[i].append(p)

    def create_cum_prob(self) -> None:
        """
        From an adjacency list with transition probabilities, calculate
        the cumulative probabilities.
        :param adjacency_list: Adjacency list with probabilities.
        :returns: Cummulative probabilities for each item in the adjacency list.
        """

        # make sure the adjacency list has been initialised
        if not hasattr(self, 'adjacency_list'):
            raise AttributeError('Attribute adjacency_list not found. Make sure'
                                 'to run create_adjacency_list first.')

        self.cum_prob: Dict[str, np.array] = {}

        for key in self.adjacency_list:
            self.cum_prob[key] = np.array(self.adjacency_list[key]).cumsum()

    @staticmethod
    def calc_trip_count_change(pre_data: NetworkData,
                               post_data: NetworkData) -> TRIP_COUNT_CHANGE:

        # percentage change of number of trips: post / pre
        trip_count_change = {}

        for cbg in pre_data.ordered_cbgs:

            if cbg in pre_data.trip_counts and cbg in post_data.trip_counts:
                change = post_data.trip_counts[cbg] / pre_data.trip_counts[cbg]

            else:
                change = 1

            trip_count_change[cbg] = change

        return trip_count_change

