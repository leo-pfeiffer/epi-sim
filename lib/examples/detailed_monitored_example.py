from typing import Any

from epydemic import SIR, Monitor, ERNetwork, StochasticDynamics, CompartmentedNodeLocus
from epyc import Experiment
from matplotlib import pyplot as plt


class DetailedMonitor(Monitor):

    def __init__(self):
        super().__init__()

    def observe(self, t: float, e: Any):
        """
        Override observe method to track not just the size of the loci but
        also the nodes in each loci.
        """
        super().observe(t, e)

        # track the actual nodes in the compartments not just the size
        for (n, l) in self.dynamics().loci().items():
            if isinstance(l, CompartmentedNodeLocus):
                name = Monitor.timeSeriesForLocus(n) + '.nodes'
                if name in self._timeSeries:
                    self._timeSeries[name].append(list(l))
                else:
                    self._timeSeries[name] = [list(l)]


class MonitoredSIR(SIR, DetailedMonitor):

    def __init__(self):
        super().__init__()

    def build(self, params):
        """Build the process, adding additional loci
        to be monitored.

        :param params: the parameters"""
        super().build(params)

        # add loci for the other compartments
        self.trackNodesInCompartment(SIR.SUSCEPTIBLE)
        self.trackNodesInCompartment(SIR.REMOVED)


if __name__ == '__main__':
    params = dict()

    # use an ER network as the substrate
    T = 1000
    params[ERNetwork.N] = N = 10000
    params[ERNetwork.KMEAN] = kmean = 3

    # set the parameters the same as above
    params[SIR.P_INFECT] = pInfect = 0.02  # infection probability
    params[SIR.P_REMOVE] = pRemove = 0.002  # recovery probability
    params[SIR.P_INFECTED] = pInfected = 0.01  # initial fraction infected

    # capture every 10 timesteps
    params[Monitor.DELTA] = 10

    # run the compound process
    e = StochasticDynamics(MonitoredSIR(), g=ERNetwork())
    e.process().setMaximumTime(T)
    rc = e.set(params).run()

    res = rc[Experiment.RESULTS]
    ts = res[Monitor.OBSERVATIONS]
    er_sss = list(map(lambda v: v / N, res[Monitor.timeSeriesForLocus(SIR.SUSCEPTIBLE)]))
    er_iis = list(map(lambda v: v / N, res[Monitor.timeSeriesForLocus(SIR.INFECTED)]))
    er_rrs = list(map(lambda v: v / N, res[Monitor.timeSeriesForLocus(SIR.REMOVED)]))

    fig = plt.figure(figsize=(5, 5))
    ax = fig.gca()
    plt.title(
        f'Progress over an ER network \n $(N = {N}, \\langle k \\rangle = {kmean})$')
    plt.xlabel('time')
    ax.set_xlim([0, T])
    plt.ylabel('fraction of population that is...')
    ax.set_ylim([0.0, 1.0])
    plt.plot(ts, er_sss, 'y', label='susceptible')
    plt.plot(ts, er_iis, 'r', label='infected')
    plt.plot(ts, er_rrs, 'g', label='removed')
    plt.legend(loc='upper right')
    plt.show()
