# Unit tests for network generators
from model.network import PowerLawCutoffNetwork


def test_create_plc():
    params = {'PLC.n': 100, 'PLC.tau': 0.2, 'PLC.kappa': 10}
    plc = PowerLawCutoffNetwork(params)
    assert plc


def test_plc_generate():
    # todo
    ...


def test_plc_topology():
    # todo
    ...
