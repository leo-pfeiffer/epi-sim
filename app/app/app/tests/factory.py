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
