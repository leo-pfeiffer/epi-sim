from typing import Dict, Union, Tuple, List
from numpy.random import Generator
from numpy import array

RANDOM_SEED = Union[Generator, int]
TRIP_COUNT_CHANGE = Dict[str, float]
COMB_COUNTS = Dict[Tuple[str, str], int]
TRIP_COUNTS = Dict[str, int]
ADJACENCY_LIST = Dict[str, List[float]]
CUM_PROB = Dict[str, array]