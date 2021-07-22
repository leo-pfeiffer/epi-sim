from typing import List
import numpy as np
import pandas as pd


def df_group_mean(df):
    grouped = df.groupby(['time', 'compartment']).mean()
    grouped.reset_index(inplace=True)
    return grouped


def epidemic_size_per_param(df, param):

    time_max = df.groupby(['experiment_id', param]).agg(
        time_max=pd.NamedAgg(column='time', aggfunc='max')
    ).to_dict()['time_max']

    filtered = df[df.apply(
        lambda x: np.isclose(time_max[(x['experiment_id'], x[param])], x['time']) and
                  x['compartment'] in ['R', 'E'], axis=1)]

    epidemic_size = filtered.groupby(
        ['experiment_id', param]
    ).value.sum()

    epidemic_size = epidemic_size.reset_index()
    epidemic_size.rename(columns={'value': 'epidemic_size'}, inplace=True)

    return epidemic_size[[param, 'epidemic_size']]


def calc_perc_infected(df):
    r = df[df.compartment == 'R'].iloc[0]['value']
    e = df[df.compartment == 'E'].iloc[0]['value']
    return r + e


def calc_susceptible_remaining(df):
    return df[df.compartment == 'S'].iloc[-1]['value']


def calc_peak_time(df):
    return df.loc[df[df.compartment == 'I'].value.idxmax(), 'time']


def calc_peak_infected(df):
    return df[df.compartment == 'I'].value.max()


def calc_effective_end(df):
    # first time, infected is sub 1% again
    infected = df[df.compartment == 'I']

    idx = find_sub_threshold_after_peak(infected.value.tolist(), 0.01)

    if idx is None:
        return None

    return infected.time.values[idx]


def find_sub_threshold_after_peak(l: List, v: float):
    """
    Find the index of the value in a list that is below a threshold  for the
    first time after a value above the peak. If the condition is not met for
    any values, return 0 if the first value of the list is below the threshold
    or None if the first value is above the threshold.
    :param l: List of values
    :param v: Threshold value
    :return: Index or None
    """
    for i in range(1, len(l)):
        if l[i - 1] > v >= l[i]:
            return i

    return 0 if l[0] <= v else None
