from lib.model.compartmental_model.seir import SEIRWithQuarantine, \
    MonitoredSEIR, MonitoredSEIRWithQuarantine
from epydemic import ERNetwork, StochasticDynamics, NetworkExperiment, Monitor

PARAMS = dict()
PARAMS[ERNetwork.N] = N = 1000
PARAMS[ERNetwork.KMEAN] = k_mean = 3
PARAMS[SEIRWithQuarantine.P_EXPOSED] = 0.01
PARAMS[SEIRWithQuarantine.P_INFECT_SYMPTOMATIC] = 0.01
PARAMS[SEIRWithQuarantine.P_INFECT_ASYMPTOMATIC] = 0.01
PARAMS[SEIRWithQuarantine.P_SYMPTOMS] = 0.01
PARAMS[SEIRWithQuarantine.P_REMOVE] = 0.005
PARAMS[SEIRWithQuarantine.P_QUARANTINE] = 0.2
PARAMS[Monitor.DELTA] = 10


def test_seir_with_quarantine():
    e = StochasticDynamics(SEIRWithQuarantine(), g=ERNetwork())
    e.set(params=PARAMS)
    rc = e.run(fatal=True)
    assert rc[NetworkExperiment.METADATA][NetworkExperiment.STATUS]

    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.SUSCEPTIBLE] > 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.INFECTED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.EXPOSED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.REMOVED] > 0

    N_is = 0
    for c in e._process.compartments():
        N_is += rc[NetworkExperiment.RESULTS][c]

    assert N_is == N


def test_monitored_seir():
    e = StochasticDynamics(MonitoredSEIR(), g=ERNetwork())
    e.set(params=PARAMS)
    rc = e.run(fatal=True)
    assert rc[NetworkExperiment.METADATA][NetworkExperiment.STATUS]

    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.SUSCEPTIBLE] > 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.INFECTED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.EXPOSED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.REMOVED] > 0

    N_is = 0
    for c in e._process.compartments():
        N_is += rc[NetworkExperiment.RESULTS][c]

    assert N_is == N


def test_monitored_seir_with_quarantine():
    e = StochasticDynamics(MonitoredSEIRWithQuarantine(), g=ERNetwork())
    e.set(params=PARAMS)
    rc = e.run(fatal=True)
    assert rc[NetworkExperiment.METADATA][NetworkExperiment.STATUS]

    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.SUSCEPTIBLE] > 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.INFECTED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.EXPOSED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIRWithQuarantine.REMOVED] > 0

    N_is = 0
    for c in e._process.compartments():
        N_is += rc[NetworkExperiment.RESULTS][c]

    assert N_is == N
