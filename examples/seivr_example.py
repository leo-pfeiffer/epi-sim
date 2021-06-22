from epydemic import ERNetwork, StochasticDynamics
import matplotlib.pyplot as plt
from epyc import Experiment

from model.compartmental_model.seivr import MonitoredSEIVR

params = dict()

T = 1000
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

# capture every 10 timesteps
params[Monitor.DELTA] = 10

# run the compound process
e = StochasticDynamics(MonitoredSEIVR(), g=ERNetwork())
e.process().setMaximumTime(T)
rc = e.set(params).run()

res = rc[Experiment.RESULTS]

if not rc[Experiment.METADATA][Experiment.STATUS]:
    raise BaseException('You fool.')

ts = res[Monitor.OBSERVATIONS]
er_sss = [v / N for v in res[Monitor.timeSeriesForLocus(SEIVR.SUSCEPTIBLE)]]
er_ees = [v / N for v in res[Monitor.timeSeriesForLocus(SEIVR.EXPOSED)]]
er_iis = [v / N for v in res[Monitor.timeSeriesForLocus(SEIVR.INFECTED)]]
er_vvs = [v / N for v in res[Monitor.timeSeriesForLocus(SEIVR.VACCINATED)]]
er_rrs = [v / N for v in res[Monitor.timeSeriesForLocus(SEIVR.REMOVED)]]

fig = plt.figure(figsize=(5, 5))
ax = fig.gca()
plt.title(f'Progress over an ER network \n $(N = {N})$')
plt.xlabel('time')
ax.set_xlim([0, T])
plt.ylabel('fraction of population that is...')
ax.set_ylim([0.0, 1.0])
plt.plot(ts, er_sss, 'y', label='susceptible')
plt.plot(ts, er_ees, 'r', label='exposed')
plt.plot(ts, er_iis, 'b', label='infected')
plt.plot(ts, er_vvs, 'm', label='vaccinated')
plt.plot(ts, er_rrs, 'g', label='removed')
plt.legend(loc='upper right')
plt.show()