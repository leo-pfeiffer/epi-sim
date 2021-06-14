import pytest
from model.network import PowerLawCutoffNetwork


@pytest.fixture()
def plc_distribution(tau=0.2, kappa=10):
    return PowerLawCutoffNetwork.distribution(tau=tau, kappa=kappa)


@pytest.fixture()
def plc(n=100, tau=0.2, kappa=10):
    params = {
        PowerLawCutoffNetwork.N: n,
        PowerLawCutoffNetwork.TAU: tau,
        PowerLawCutoffNetwork.KAPPA: kappa
    }
    return PowerLawCutoffNetwork(params)
