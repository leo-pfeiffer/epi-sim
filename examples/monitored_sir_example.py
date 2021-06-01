from epydemic import SIR, ProcessSequence, Monitor, ERNetwork, StochasticDynamics
from epyc import Experiment
from matplotlib import pyplot as plt


class MonitoredSIR(SIR):

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

    # build a compund process from the disease and the monitor
    p = ProcessSequence([MonitoredSIR(), Monitor()])

    # run the compound process
    e = StochasticDynamics(p, g=ERNetwork())
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