from lib.model.network.mobility_network import MobilityNetwork
from lib.model.network.network_data import NetworkData
from lib.model.distributions import PowerLawCutoffDist


def create_cbgs():
    return [f'cbg{i}' for i in range(1, 11)]


def create_demographics():
    cbgs = create_cbgs()

    population = [i for i in range(1, len(cbgs) + 1)]
    population_prop = [p / sum(population) for p in population]

    household_size = [3 for _ in range(len(cbgs))]

    demographics = {}
    for i, cbg in enumerate(cbgs):
        demographics[cbg] = {}
        demographics[cbg]['population_prop'] = population_prop[i]
        demographics[cbg]['household_size'] = household_size[i]

    return demographics


def create_counts(post: bool = False):
    cbgs = create_cbgs()

    comb_counts = {}
    trip_counts = {}
    for i, cbg1 in enumerate(cbgs):
        for j, cbg2 in enumerate(cbgs):

            count = i + j + 2

            if post:
                count //= 2

            comb_counts[(cbg1, cbg2)] = count

            if cbg2 in trip_counts:
                trip_counts[cbg2] += count
            else:
                trip_counts[cbg2] = count

    return comb_counts, trip_counts


def create_network_data(post: bool = False):
    demographics = create_demographics()
    comb_counts, trip_counts = create_counts(post)
    network_data = NetworkData(demographics, comb_counts, trip_counts)
    return network_data


def create_network_graph():
    exponent = 2
    cutoff = 10
    n = 1000
    pre = create_network_data()

    pre.create_adjacency_list()
    pre.create_cum_prob()

    degree_dist = PowerLawCutoffDist(exponent, cutoff).p

    network = MobilityNetwork(pre, degree_dist, n, False)
    network.create()
    return network.g
