import networkx as nx


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


def calc_shortest_paths(graph: nx.Graph) -> list[int]:
    """
    Calculate the shortest path distances of a graph.
    :param graph: The graph.
    :return: List with shortest path lengths.
    """
    shortest_paths = []
    for x in nx.shortest_path_length(graph):
        shortest_paths.extend(list(x[1].values()))
    return shortest_paths


def calc_cluster_coeff(graph: nx.Graph) -> list[float]:
    """
    Calculate the cluster coefficients of the nodes of a graph.
    :param graph: The graph.
    :return: List with cluster coefficients.
    """
    coefficients = nx.clustering(graph)
    return list(coefficients.values())


def calc_degrees(graph: nx.Graph) -> list[int]:
    """
    Get the the node degrees of a graph.
    :param graph: The graph.
    :return: List of degrees.
    """
    return list(dict(graph.degree).values())
