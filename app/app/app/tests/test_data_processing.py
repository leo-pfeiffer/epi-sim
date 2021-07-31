from .factory import *
from ..data_processing import SimulationData, EmpiricalData, ModelledData
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


def test_extract_region():

    states = ['CT', 'CA', 'FL']
    state_names = ['Connecticut', 'California', 'Florida']
    pop = ['10,000.0', '20,000.0', '30,000.0']

    df = pd.DataFrame({
        'state_name': state_names,
        'population': pop,
        'state': states
    })

    extracted = EmpiricalData.extract_region(
        df, {'column': 'state', 'value': 'CT'}
    )

    assert extracted.state.unique()[0] == 'CT'
    assert len(extracted) == 1


def test_get_data_after_date():

    dates = [
        np.datetime64('2021-01-20'),
        np.datetime64('2021-01-25'),
        np.datetime64('2021-02-01')
    ]

    df = pd.DataFrame({'my_date': dates, 'col': [1, 2, 3]})

    after = EmpiricalData.get_data_after_date(
        df, '2021-01-25', date_col='my_date'
    )

    assert len(after) == 2
    assert np.datetime64('2021-01-20') not in after.my_date.values


def test_make_counts_relative():

    tot_c = [100, 200, 300]
    new_c = [10, 20, 30]
    p = 100

    df = pd.DataFrame({'tot_cases': tot_c, 'new_cases': new_c})

    relative = EmpiricalData.make_counts_relative(df, p)

    for i in range(len(relative)):
        assert relative.tot_cases.values[i] == pytest.approx(tot_c[i] / p)
        assert relative.new_cases.values[i] == pytest.approx(new_c[i] / p)


def test_make_first_wave_map():
    dates = ['01/01/2021', '02/01/2021', '03/01/2021'] * 3
    tot_c = ['10,000.0', '20,000.0', '30,000.0'] * 3
    new_c = ['5'] * 9
    states = ['CT'] * 3 + ['CA'] * 3 + ['FL'] * 3

    covid_df = EmpiricalData.transform_covid(pd.DataFrame({
        'date': dates,
        'tot_cases': tot_c,
        'new_cases': new_c,
        'state': states
    }))

    pop_map = EmpiricalData.make_state_population(
        pd.DataFrame({
            'state_name': ['Connecticut', 'California', 'Florida'],
            'population': ['20,000.0', '40,000.0', '60,000.0'],
            'state': ['CT', 'CA', 'FL']
        })
    )

    first_wave = EmpiricalData.make_first_wave_map(
        covid_df, pop_map, 0.5
    )

    assert first_wave['CT'] == '2021-01-01'
    assert first_wave['CA'] == '2021-02-01'
    assert first_wave['FL'] == '2021-03-01'


def test_calc_cases():

    new_case_diff = [40, 40, 20, 10]
    tot_cases = [19, 20, 21, 22]

    data = {
        'S': [80, 40, 20, 10],
        'E': [5, 5, 5, 5],
        'I': [6, 6, 6, 6],
        'V': [7, 7, 7, 7],
        'R': [8, 9, 10, 11],
    }

    seir = ModelledData.calc_cases(pd.DataFrame(data), 'seir')
    seirq = ModelledData.calc_cases(pd.DataFrame(data), 'seir_q')

    assert 'new_cases' in seir.columns
    assert 'tot_cases' in seir.columns

    assert 'new_cases' in seirq.columns
    assert 'tot_cases' in seirq.columns

    for i in range(len(seir)):
        assert seir.new_cases.values[i] == new_case_diff[i]
        assert seir.tot_cases.values[i] == tot_cases[i]
        assert seirq.new_cases.values[i] == new_case_diff[i]
        assert seirq.tot_cases.values[i] == tot_cases[i]

    seivr = ModelledData.calc_cases(pd.DataFrame(data), 'seivr')
    seivrq = ModelledData.calc_cases(pd.DataFrame(data), 'seivr_q')

    assert 'new_cases' not in seivr.columns
    assert 'tot_cases' in seivr.columns

    assert 'new_cases' not in seivrq.columns
    assert 'tot_cases' in seivrq.columns

    for i in range(len(seir)):
        assert seivr.tot_cases.values[i] == tot_cases[i]
        assert seivrq.tot_cases.values[i] == tot_cases[i]
