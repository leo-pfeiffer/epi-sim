from typing import Dict, Any
import numpy as np
import pandas as pd


class SimulationTransformerMixin:
    """
    Transformer Mixin that contains methods to transform simulation data.
    """

    @staticmethod
    def _apply_filters(df, filters: Dict[str, Any]):
        """
        Filter `df` by the conditions provided in `filters` where the keys
        correspond to columns in `df` and values are the values to filter for.
        :param df: Data frame to filter
        :param filters: Dictionary with filter conditions
        :return: filtered df
        """
        # create array with true values only
        arr = np.array([True] * len(df))

        for k, v in filters.items():
            # define filter (taking into account floating point imprecision) and
            #  combine with previous filters
            arr = arr & (lambda x: np.isclose(x, v))(df[k].values)

        return df.loc[arr]

    @staticmethod
    def fill_experiment_length_gap(df, delta: int = 10):
        """
        If an experiment earlier than others, propagate (forward fill)
        the last row's results up until that time. This is necessary if we
        calculate the mean value per time step, since experiments that
        end early would mess with the calculations beyond that time step.
        :param df: Simulation data frame.
        :param delta: (optional) Delta between time steps.
        :return: Data frame with propagated experiments.
        """

        assert delta >= 1

        # lists that will hold the values that we need to fill in
        ls_experiment_id = []
        ls_time = []
        ls_compartment = []
        ls_value = []

        # duration of longest experiment
        max_time = int(max(df.time.values))

        # do for each experiment
        for exp in df.experiment_id.unique():

            exp_df = df[df.experiment_id == exp]
            last_time = max(exp_df.time.values)

            # don't need to do anything if there's no gap
            if last_time >= max_time:
                continue

            # grid with length 10
            fill_gap = [*range(int(last_time) + delta, max_time + 1, delta)]

            # get last value of each compartment
            values = []
            compartments = exp_df.compartment.unique()
            for c in compartments:
                v = exp_df[(exp_df['time'] == last_time) &
                           (exp_df['compartment'] == c)].iloc[0].at['value']
                values.extend([v] * len(fill_gap))

            # extend the lists
            ls_experiment_id.extend([exp] * len(fill_gap) * len(compartments))

            ls_time.extend(fill_gap * len(compartments))

            ls_compartment.extend(
                sum([[c] * len(fill_gap) for c in compartments], [])
            )

            ls_value.extend(values)

        # data frame with all gap values
        fill_df = pd.DataFrame({
            'experiment_id': ls_experiment_id,
            'time': ls_time,
            'compartment': ls_compartment,
            'value': ls_value
        })

        if fill_df.empty:
            return df

        # concatenate everything, fill params, reset index, and we're done
        df = pd.concat([fill_df, df])
        df = df.fillna(method='ffill', axis=1).fillna(method='bfill', axis=1)
        df = df.reset_index(drop=True)

        return df

    @staticmethod
    def df_group_mean(df):
        """
        Calculate the mean value per time per compartment.
        :param df: Simulation df.
        :return: grouped data frame.
        """
        grouped = df.groupby(['time', 'compartment']).mean()
        grouped.reset_index(inplace=True)
        return grouped
