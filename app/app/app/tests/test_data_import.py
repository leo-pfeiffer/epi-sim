from factory import create_simulation_df
from ..data_import import SimulationData


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