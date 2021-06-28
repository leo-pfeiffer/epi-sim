from model.compartmental_model.seivr import SEIVRWithQuarantine, SEIVR
from epydemic import ERNetwork, StochasticDynamics, NetworkExperiment

PARAMS = dict()
PARAMS[ERNetwork.N] = N = 1000
PARAMS[ERNetwork.KMEAN] = k_mean = 3
PARAMS[SEIVRWithQuarantine.P_EXPOSED] = 0.01
PARAMS[SEIVRWithQuarantine.P_INFECT_SYMPTOMATIC] = 0.01
PARAMS[SEIVRWithQuarantine.P_INFECT_ASYMPTOMATIC] = 0.01
PARAMS[SEIVRWithQuarantine.P_SYMPTOMS] = 0.01
PARAMS[SEIVRWithQuarantine.P_REMOVE] = 0.005
PARAMS[SEIVRWithQuarantine.P_VACCINATED_INITIAL] = 0.0
PARAMS[SEIVRWithQuarantine.P_VACCINATED] = 0.005
PARAMS[SEIVRWithQuarantine.VACCINE_RRR] = 0.75
PARAMS[SEIVRWithQuarantine.P_QUARANTINE] = 0.2


def test_seivr():
    e = StochasticDynamics(SEIVR(), g=ERNetwork())
    e.set(params=PARAMS)
    rc = e.run(fatal=True)
    assert rc[NetworkExperiment.METADATA][NetworkExperiment.STATUS]

    assert rc[NetworkExperiment.RESULTS][SEIVR.SUSCEPTIBLE] >= 0
    assert rc[NetworkExperiment.RESULTS][SEIVR.INFECTED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIVR.EXPOSED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIVR.VACCINATED] > 0
    assert rc[NetworkExperiment.RESULTS][SEIVR.REMOVED] >= 0

    assert sum(rc[NetworkExperiment.RESULTS].values()) == N


def test_seivr_with_quarantine():
    e = StochasticDynamics(SEIVRWithQuarantine(), g=ERNetwork())
    e.set(params=PARAMS)
    rc = e.run(fatal=True)
    assert rc[NetworkExperiment.METADATA][NetworkExperiment.STATUS]

    assert rc[NetworkExperiment.RESULTS][SEIVRWithQuarantine.SUSCEPTIBLE] >= 0
    assert rc[NetworkExperiment.RESULTS][SEIVRWithQuarantine.INFECTED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIVRWithQuarantine.EXPOSED] == 0
    assert rc[NetworkExperiment.RESULTS][SEIVRWithQuarantine.VACCINATED] > 0
    assert rc[NetworkExperiment.RESULTS][SEIVRWithQuarantine.REMOVED] >= 0

    assert sum(rc[NetworkExperiment.RESULTS].values()) == N

