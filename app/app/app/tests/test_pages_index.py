from .factory import create_simulation_df
import pandas as pd
from ..calculations import df_group_mean, epidemic_size_per_param, \
    calc_perc_infected, calc_susceptible_remaining, calc_peak_time, \
    calc_peak_infected, calc_effective_end, find_sub_threshold_after_peak


def test_df_group_mean():
    df = create_simulation_df('SEIR')
    df2 = pd.concat([df, df]).reset_index(drop=True)

    # taking the mean should give same result even if we use the same df twice
    assert df_group_mean(df2).equals(df_group_mean(df))


def test_epidemic_size_per_param():
    df = create_simulation_df('SEIR')
    es = epidemic_size_per_param(df, 'param')
    assert es['param'][0] == 0.2
    assert es['epidemic_size'][0] == 0.001 * 2


def test_calc_perc_infected():
    df = create_simulation_df('SEIR')
    assert calc_perc_infected(df) == 0.01 + 0.01


def test_calc_susceptible_remaining():
    df = create_simulation_df('SEIR')
    assert calc_susceptible_remaining(df) == 0.001


def test_calc_peak_time():
    df = create_simulation_df('SEIR')
    assert calc_peak_time(df) == 2


def test_calc_peak_infected():
    df = create_simulation_df('SEIR')
    assert calc_peak_infected(df) == 0.5


def test_calc_effective_end():
    df = create_simulation_df('SEIR')
    assert calc_effective_end(df) == 8


def test_find_sub_threshold_after_peak():
    t = 1
    l1 = [0.1, 0.5, 1.3, 0.8, 0.7]  # 3
    l2 = [0.1, 0.5, 0.7, 1.2, 0.7]  # 4
    l3 = [0.1, 0.5, 0.7, 0.7, 0.7]  # 0
    l4 = [1.1, 1.2, 1.3, 1.4, 1.5]  # None
    l5 = [0.1, 1.1, 0.7, 1.2, 0.7]  # 2

    assert find_sub_threshold_after_peak(l1, t) == 3
    assert find_sub_threshold_after_peak(l2, t) == 4
    assert find_sub_threshold_after_peak(l3, t) == 0
    assert find_sub_threshold_after_peak(l4, t) is None
    assert find_sub_threshold_after_peak(l5, t) == 2
