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
        simulation.current_state = {'model': '', 'network': '', 'filters': ''}

    # can't set wrong keys
    with pytest.raises(AssertionError):
        simulation.current_state = {'some_key': '', 'network': '', 'filters': {}}

    # this should work
    should = {'model': '', 'network': '', 'filters': {1: 2}}
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


def test_apply_filters():
    df = create_simulation_df('SEIR', True)
    f1 = {'param': 0.2}  # all
    f2 = {'param': 0.3}  # none
    f3 = {'param': 0.2, 'param2': 0.1}  # 4
    f4 = {'param': 0.2, 'param2': 1}  # None

    assert SimulationData._apply_filters(df, f1).equals(df)
    assert SimulationData._apply_filters(df, f2).empty

    assert len(SimulationData._apply_filters(df, f3)) == 4
    assert all([x[1].param == f3['param'] and x[1].param2 == f3['param2']
                for x in SimulationData._apply_filters(df, f3).iterrows()])

    assert SimulationData._apply_filters(df, f4).empty


def test_df_group_mean():
    df = create_simulation_df('SEIR')
    df2 = pd.concat([df, df]).reset_index(drop=True)

    # taking the mean should give same result even if we use the same df twice
    df_mean1 = SimulationData.df_group_mean(df)
    df_mean2 = SimulationData.df_group_mean(df2)
    assert df_mean1.equals(df_mean2)


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


def test_fill_experiment_length_gap():
    model = 'SEIR'
    exp_lengths = [10, 20, 30]
    df = create_uneven_experiment_simulation_df(model, exp_lengths)

    # make sure the setup is correct...
    assert len(df) == len(model) * sum(exp_lengths)
    for c in model:
        assert len(df[df['compartment'] == c]) == sum(exp_lengths)

    # do the transformation
    filled = SimulationData.fill_experiment_length_gap(df, delta=1)

    # assert the format is correct
    el = len(exp_lengths) * max(exp_lengths)
    assert len(filled) == len(model) * el
    for c in model:
        assert len(filled[filled['compartment'] == c]) == el

    # assert the correct values were propagated
    for e in range(len(exp_lengths)):
        for c in model:
            orig_sub = df[(df.experiment_id == e) & (df.compartment == c)]
            orig_max_t = max(orig_sub.time)
            max_val = orig_sub[orig_sub.time == orig_max_t].iloc[0].at['value']

            new_sub = filled[(filled.experiment_id == e) & (filled.compartment == c)]
            new_max_t = max(new_sub.time)

            # correct new max time
            assert new_max_t == max(exp_lengths) - 1

            # "new" part of the data frame
            new_part = new_sub[new_sub.time > orig_max_t]

            # make sure all propagated values correspond to original max value
            for v in new_part.value.values:
                assert v == max_val

