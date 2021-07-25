from .factory import create_simulation_df
from ..data_processing import SimulationData

import pandas as pd


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


def test_calc_susceptible_remaining():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_susceptible_remaining(df) == 0.001


def test_calc_peak_time():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_peak_time(df) == 2


def test_calc_peak_infected():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_peak_infected(df) == 0.5


def test_calc_effective_end():
    df = create_simulation_df('SEIR')
    assert SimulationData.calc_effective_end(df) == 8


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
