from epyc import Experiment
from epydemic import ERNetwork, StochasticDynamics, Monitor

from lib.model.compartmental_model.seivr import MonitoredSEIVR, SEIVR
from matplotlib import pyplot as plt


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


params = dict()

# use an ER network as the substrate
params[ERNetwork.N] = N = 10000
params[ERNetwork.KMEAN] = k_mean = 3

# set the parameters the same as above
params[SEIVR.P_EXPOSED] = 0.001
params[SEIVR.P_INFECT_ASYMPTOMATIC] = 0.01
params[SEIVR.P_INFECT_SYMPTOMATIC] = 0.02
params[SEIVR.P_REMOVE] = 0.002
params[SEIVR.P_SYMPTOMS] = 0.002
params[SEIVR.P_VACCINATED_INITIAL] = 0.0
params[SEIVR.P_VACCINATED] = 0.0002
params[SEIVR.VACCINE_RRR] = 0.95

# capture every 10 time steps
params[Monitor.DELTA] = 10

# run the compound process
e = StochasticDynamics(MonitoredSEIVR(), g=ERNetwork())

compartments = {
    SEIVR.SUSCEPTIBLE: 'susceptible',
    SEIVR.EXPOSED: 'exposed',
    SEIVR.INFECTED: 'infected',
    SEIVR.VACCINATED: 'vaccinated',
    SEIVR.REMOVED: 'removed'
}

T = 1000

e.process().setMaximumTime(T)
e.set(params)
rc = e.run()
result = rc[Experiment.RESULTS]

times = result[Monitor.OBSERVATIONS]
series = dict()

_N = 0
for c in compartments:
    _N += result[c]

for c in compartments:
    series_abs = result[Monitor.timeSeriesForLocus(c)]
    series_rel = [v / _N for v in series_abs]
    series[c] = series_rel

color_gen = _color_string()

fig = plt.figure(figsize=(5, 5))
ax = fig.gca()
plt.title('Title')
plt.xlabel('time')
ax.set_xlim([0, T])
ax.set_ylim([0.0, 1.0])
plt.ylabel('fraction of population')

for c in compartments:
    plt.plot(times, series[c], next(color_gen), label=compartments[c])

plt.legend(loc='upper right')
plt.show()

