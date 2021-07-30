from .factory import *
from ..mixins import SimulationTransformerMixin as STM


def test_apply_filters():
    df = create_simulation_df('SEIR', True)
    f1 = {'param': 0.2}  # all
    f2 = {'param': 0.3}  # none
    f3 = {'param': 0.2, 'param2': 0.1}  # 4
    f4 = {'param': 0.2, 'param2': 1}  # None

    assert STM._apply_filters(df, f1).equals(df)
    assert STM._apply_filters(df, f2).empty

    assert len(STM._apply_filters(df, f3)) == 4
    assert all([x[1].param == f3['param'] and x[1].param2 == f3['param2']
                for x in STM._apply_filters(df, f3).iterrows()])

    assert STM._apply_filters(df, f4).empty


def test_df_group_mean():
    df = create_simulation_df('SEIR')
    df2 = pd.concat([df, df]).reset_index(drop=True)

    # taking the mean should give same result even if we use the same df twice
    df_mean1 = STM.df_group_mean(df)
    df_mean2 = STM.df_group_mean(df2)
    assert df_mean1.equals(df_mean2)


def test_fill_experiment_length_gap():
    model = 'SEIR'
    exp_lengths = [10, 20, 30]
    df = create_uneven_experiment_simulation_df(model, exp_lengths)

    # make sure the setup is correct...
    assert len(df) == len(model) * sum(exp_lengths)
    for c in model:
        assert len(df[df['compartment'] == c]) == sum(exp_lengths)

    # do the transformation
    filled = STM.fill_experiment_length_gap(df, delta=1)

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

            new_sub = filled[
                (filled.experiment_id == e) & (filled.compartment == c)
            ]
            new_max_t = max(new_sub.time)

            # correct new max time
            assert new_max_t == max(exp_lengths) - 1

            # "new" part of the data frame
            new_part = new_sub[new_sub.time > orig_max_t]

            # make sure all propagated values correspond to original max value
            for v in new_part.value.values:
                assert v == max_val

