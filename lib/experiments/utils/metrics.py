# This file defines a class for an epyc MetricExperiment to calculate
#  network metrics for a given network.

import sys
from typing import Union, List
if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final


import networkx as nx
from epydemic import NetworkExperiment, NetworkGenerator
from networkx import Graph


class MetricExperiment(NetworkExperiment):
    """
    A MetricExperiment to compute metrics of a given network using epyc.
    """

    # Generator
    GENERATOR: Final[str] = 'metric.generator'

    def __init__(self, g: Union[Graph, NetworkGenerator] = None):
        super(MetricExperiment, self).__init__(g)

    def do(self, params):

        densities = calc_density(self.network())
        cluster_coeffs = calc_cluster_coeff(self.network())
        degrees = calc_degrees(self.network())

        # to computationally expensive ...
        # shortest_paths = calc_shortest_paths(self.network())

        result = dict(
            densities=densities,
            cluster_coeffs=cluster_coeffs,
            degrees=degrees,
            # shortest_paths=shortest_paths,
        )

        return result


def calc_density(graph: nx.Graph) -> float:
    """
    Calculate the node density of a graph.
    :param graph: The graph.
    :return: The density.
    """
    num_edges = len(graph.edges)
    num_nodes = len(graph.nodes)
    num_edges_max = num_nodes * (num_nodes - 1) / 2
    return num_edges / num_edges_max


def calc_shortest_paths(graph: nx.Graph) -> List[int]:
    """
    Calculate the shortest path distances of a graph.
    :param graph: The graph.
    :return: List with shortest path lengths.
    """
    shortest_paths = []
    for x in nx.shortest_path_length(graph):
        shortest_paths.extend(list(x[1].values()))
    return shortest_paths


def calc_cluster_coeff(graph: nx.Graph) -> List[float]:
    """
    Calculate the cluster coefficients of the nodes of a graph.
    :param graph: The graph.
    :return: List with cluster coefficients.
    """
    coefficients = nx.clustering(graph)
    return list(coefficients.values())


def calc_degrees(graph: nx.Graph) -> List[int]:
    """
    Get the the node degrees of a graph.
    :param graph: The graph.
    :return: List of degrees.
    """
    return list(dict(graph.degree).values())
