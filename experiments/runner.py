from typing import Any, Dict, Union, List, Tuple, Iterable
from epyc import ResultsDict, Experiment
from epydemic import Dynamics, Monitor

from matplotlib import pyplot as plt
import pandas as pd


class ExperimentRunner:
    """
    Wrapper around the epydemic `Dynamics` (sub-)classes to streamline some
    of the code required for running a single experiment and plotting the
    result.
    """

    def __init__(self, dynamics: Dynamics):
        """
        Constructor.
        :param dynamics: Dynamics of the experiment.
        :param N: Size of the network... for convenience since this way we don't
            have to awkwardly try to access the network.
        """
        self._dynamics = dynamics
        self._N: int = 0
        self._result: Union[ResultsDict, None] = None

    @property
    def dynamics(self):
        return self._dynamics

    @property
    def result(self):
        return self._result

    @property
    def n(self):
        return self._N

    def run(self, params: Dict[str, Any], T: int = 1000, fatal: bool = True):
        """
        Run the experiment
        :param params: Experiment parameters
        :param T: Maximum time of the experiment
        :param fatal: If True, exceptions in the experiment are raised. Else
            they are stored in the results dict.
        """

        self._dynamics.process().setMaximumTime(T)
        self._dynamics.set(params)
        rc = self._dynamics.run(fatal=fatal)
        self._result = rc[Experiment.RESULTS]

    def get_time_series(self, compartments: Iterable[str]) -> \
            Tuple[List[float], Dict[str, List[float]]]:
        """
        Get the time series of the population in the compartments specified.
        :param compartments: Any iterable of compartment keys.
        :return: List of time steps, List of time series lists
        """

        times: List[float] = self.result[Monitor.OBSERVATIONS]
        series = dict()

        for c in compartments:
            self._N += self.result[c]

        for c in compartments:
            series_abs = self.result[Monitor.timeSeriesForLocus(c)]
            series_rel = [v / self._N for v in series_abs]
            series[c] = series_rel

        return times, series

    @staticmethod
    def _color_string():
        """
        Simple color string generator. Not that if it is called more than
        `len(colors)` times, the colours are not unique.
        :return: Generator object
        """
        colors = ['r', 'c', 'g', 'm', 'b', 'y', 'peru', 'pink', 'gray']
        i = 0
        while True:
            i %= len(colors)
            yield colors[i]
            i += 1

    def plot(self, title: str, compartments: Dict[str, str]):
        """
        Plot the results of the experiment.
        :param title: Title of the plot
        :param compartments: Compartment keys with labels.
        """

        times, series = self.get_time_series(compartments.keys())
        T = self._dynamics.process().maximumTime()
        color_gen = self._color_string()

        fig = plt.figure(figsize=(5, 5))
        ax = fig.gca()
        plt.title(title)
        plt.xlabel('time')
        ax.set_xlim([0, T])
        ax.set_ylim([0.0, 1.0])
        plt.ylabel('fraction of population')

        for c in compartments:
            plt.plot(times, series[c], next(color_gen), label=compartments[c])

        plt.legend(loc='upper right')
        plt.show()

    def to_df(self, compartments, network, model):

        times, series = self.get_time_series(compartments.keys())

        values = []
        compartment_vals = []
        time_vals = []

        for k, v in compartments.items():
            values += series[k]
            compartment_vals += [v for _ in series[k]]
            time_vals += times

        df = pd.DataFrame({
            'value': values,
            'compartment': compartment_vals,
            'time': time_vals
        })

        df['network'] = network
        df['model'] = model
        df['N'] = self._N
        df['T'] = self._dynamics.process().maximumTime()

        return df

