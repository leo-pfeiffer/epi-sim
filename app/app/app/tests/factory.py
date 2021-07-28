from typing import List
import numpy as np
import pandas as pd


def create_simulation_df(model: str, has_param2: bool = False):
    T = 10
    data = {
        'experiment_id': [1] * T * len(model),
        'time': [*range(T)] * len(model),
        'compartment': sum([[c] * T for c in model], []),
        'value': [0.01, 0.1, 0.5, 0.5, 0.5, 0.4, 0.4, 0.2, 0.0015, 0.001] * len(model),
        'param': [0.2] * len(model) * T,
    }
    if has_param2:
        data['param2'] = [x / T for x in range(T)] * len(model)
    return pd.DataFrame(data)


def create_uneven_experiment_simulation_df(model: str, exp_lengths: List[int]):

    ls_experiment_id = sum([[i] * l for i, l in enumerate(exp_lengths)], []) * len(model)
    ls_time = sum([[*range(t)] for t in exp_lengths], []) * len(model)
    ls_compartment = sum(sum([[[m] * j for j in exp_lengths] for m in model], []), [])
    ls_value = [round(np.random.random(), 2) for _ in range(len(ls_time))]

    data = {
        'experiment_id': ls_experiment_id,
        'time': ls_time,
        'compartment': ls_compartment,
        'value': ls_value,
        'param': [0.2] * len(ls_value)
    }
    return pd.DataFrame(data)
