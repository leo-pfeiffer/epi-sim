from .factory import *
from ..data_processing import SimulationData
from ..simulation_files import FILES, MODELS, NETWORKS
import pytest

import pandas as pd


def test_files_property():
    simulation = SimulationData()
    assert simulation.files == FILES


def test_current_state_property():
    simulation = SimulationData()
    assert simulation.current_state == dict()

    # can't set empty dict
    with pytest.raises(AssertionError):
        simulation.current_state = {}

    # can't set filters as non-dict
    with pytest.raises(AssertionError):
        simulation.current_state = {
            'model': '', 'network': '', 'filters': '', 'disease': ''
        }

    # can't set wrong keys
    with pytest.raises(AssertionError):
        simulation.current_state = {
            'some_key': '', 'network': '', 'filters': {}
        }

    # this should work
    should = {
        'model': '', 'network': '', 'filters': {1: 2}, 'disease': ''
    }
    simulation.current_state = should
    assert simulation.current_state == should


def test_files_loaded_property():
    simulation = SimulationData()
    assert not simulation.files_loaded


def test_models_property():
    simulation = SimulationData()
    assert simulation.models == sorted(MODELS)


def test_networks_property():
    simulation = SimulationData()
    assert simulation.networks == sorted(NETWORKS)


def test_epidemic_size_per_param():
    df = create_simulation_df('SEIR')
    es = SimulationData.epidemic_size_per_param(df, 'param')
    assert es['param'][0] == 0.2
    assert es['epidemic_size'][0] == 0.001 * 2


def test_calc_perc_infected():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_perc_infected(df) == 0.01 + 0.01


def test_calc_susceptible_remaining_seir():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_susceptible_remaining(df) == 0.001


def test_calc_susceptible_remaining_seivr():
    df = create_simulation_df('SEIVR')
    assert SimulationData.calc_susceptible_remaining(df) == 0.002


def test_calc_peak_time():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_peak_time(df) == 2


def test_calc_peak_infected():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_peak_infected(df) == 0.5


def test_calc_effective_end():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_effective_end(df) == 8


def test_calc_effective_end_none():
    df = pd.DataFrame(columns=['compartment', 'value'])
    assert SimulationData.calc_effective_end(df) is None


def test_find_sub_threshold_after_peak():
    t = 1
    l1 = [0.1, 0.5, 1.3, 0.8, 0.7]  # 3
    l2 = [0.1, 0.5, 0.7, 1.2, 0.7]  # 4
    l3 = [0.1, 0.5, 0.7, 0.7, 0.7]  # 0
    l4 = [1.1, 1.2, 1.3, 1.4, 1.5]  # None
    l5 = [0.1, 1.1, 0.7, 1.2, 0.7]  # 2

    assert SimulationData.find_sub_threshold_after_peak(l1, t) == 3
    assert SimulationData.find_sub_threshold_after_peak(l2, t) == 4
    assert SimulationData.find_sub_threshold_after_peak(l3, t) == 0
    assert SimulationData.find_sub_threshold_after_peak(l4, t) is None
    assert SimulationData.find_sub_threshold_after_peak(l5, t) == 2
