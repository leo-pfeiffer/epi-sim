from __future__ import annotations

from typing import Dict, List
from dataclasses import dataclass, field

import numpy as np
from model.types import TRIP_COUNT_CHANGE, COMB_COUNTS, TRIP_COUNTS,\
    ADJACENCY_LIST, CUM_PROB


# special types for convenience...
DEMOGRAPHICS = Dict[str, Dict[str, float]]


@dataclass
class NetworkData:
    """
    Collection of mobility data required for building a MobilityNetwork.
    """

    demographics: DEMOGRAPHICS  # Demographics data
    comb_counts: COMB_COUNTS    # Count of trips between combinations of CBGs
    trip_counts: TRIP_COUNTS    # Total count of trips leaving one CBG

    # not initialised in dataclass
    ordered_cbgs: List[str] = field(init=False)  # CBGs in order
    adjacency_list: ADJACENCY_LIST = field(init=False)  # Adjacency list of CBGs
    cum_prob: CUM_PROB = field(init=False)  # Cumulative transition prob.
    trip_count_change: TRIP_COUNT_CHANGE = field(init=False)  # Trip ct change

    def __post_init__(self):
        self.ordered_cbgs = sorted(self.demographics.keys())

    def create_adjacency_list(self) -> None:
        """
        Create the adjacency list of the CBGs. The keys are the CGBs and the
        values are ordered lists of transition probabilities to other CBGs.
        The probabilities are in the same order as `ordered_cbgs`.
        The transition probability from CBG i to CBG j is
        P(i, j) = count(trips between i and j) / count(all trips leaving CBG i).
        """

        self.adjacency_list = {}

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
        Calculate the cumulative transition probabilities from the adjacency
        list. The cumulative probabilities are in the same order as the CBGs
        in `ordered_cbgs`.
        """

        # make sure the adjacency list has been initialised
        if not hasattr(self, 'adjacency_list'):
            raise AttributeError('Attribute adjacency_list not found. Make sure'
                                 'to run create_adjacency_list first.')

        self.cum_prob = {}

        for key in self.adjacency_list:
            self.cum_prob[key] = np.array(self.adjacency_list[key]).cumsum()

    def calc_trip_count_change(self, pre_data: NetworkData):
        """
        Calculate the change in trip counts compared to another NetworkData
        instance. The trip count change is saved in the `trip_count_change`
        attribute of the current instance (not of the `pre_data`).
        The use case for this is to determine the change in mobility e.g. pre
        lockdown vs post lockdown.
        :param pre_data: Base NetworkData to compare to (e.g. before lockdown).
        """

        # change in number of trips: post / pre
        trip_count_change = {}

        for cbg in pre_data.ordered_cbgs:

            # regular case: CBG present pre and post
            if cbg in pre_data.trip_counts and cbg in self.trip_counts:
                change = self.trip_counts[cbg] / pre_data.trip_counts[cbg]

            # special case: CBG not present post -> decrease by 100%
            elif cbg in pre_data.trip_counts and \
                    cbg not in self.trip_counts:
                change = 0

            # special case: CBG not present pre -> increase by 100%
            else:
                change = 2

            trip_count_change[cbg] = change

        self.trip_count_change = trip_count_change
