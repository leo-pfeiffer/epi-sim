from epydemic import ERNetwork, StochasticDynamics, Monitor

from model.compartmental_model.seivr import MonitoredSEIVR, SEIVR
from experiments.runner import ExperimentRunner

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

er = ExperimentRunner(e)
er.run(params, T=1000)
er.plot('My title', compartments)
