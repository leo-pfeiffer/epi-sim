from .factory import *
from ..data_processing import SimulationData, EmpiricalData
from ..simulation_files import FILES, MODELS, NETWORKS
import pytest

import pandas as pd
import numpy as np


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


def test_transform_covid():
    dates = ['01/25/2021', '01/20/2021', '01/26/2021']
    tot_c = ['10,000.0', '10,005.0', '10,010.0']
    new_c = ['10,000.0', '5', '5.0']

    df = pd.DataFrame({'date': dates, 'tot_cases': tot_c, 'new_cases': new_c})

    transformed = EmpiricalData.transform_covid(df)

    # date types ?
    assert pd.api.types.is_datetime64_dtype(transformed.date.dtype)
    assert pd.api.types.is_float_dtype(transformed.tot_cases.dtype)
    assert pd.api.types.is_float_dtype(transformed.new_cases.dtype)

    # sorted ?
    for i, v in enumerate(sorted(transformed.date.values.tolist())):
        assert v == int(transformed.date.values[i])


def test_make_state_population():

    states = ['CT', 'CA', 'FL']
    state_names = ['Connecticut', 'California', 'Florida']
    pop = ['10,000.0', '20,000.0', '30,000.0']

    df = pd.DataFrame({
        'state_name': state_names,
        'population': pop,
        'state': states
    })

    pop_map = EmpiricalData.make_state_population(df)

    assert pop_map['CT'] == 10000
    assert pop_map['CA'] == 20000
    assert pop_map['FL'] == 30000

    # dates = ['01/25/2021', '01/20/2021', '01/26/2021']
    # tot_c = [1, 3, 6]
    # new_c = [1, 2, 3]
    # pop = ['10,000.0', '10,000.0', '10,000.0']
    #
    # df = pd.DataFrame({
    #     'date': dates,
    #     'total_cases': tot_c,
    #     'new_cases': new_c,
    #     'population': pop
    # })