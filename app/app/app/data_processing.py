import sys
from typing import Dict, Any, List

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

import pandas as pd
import numpy as np
import pickle
from urllib.request import urlopen
import os
from tqdm import tqdm

from .configuration import DATA_REPO_URL_RAW, DATA_DIR
from .simulation_files import FILES, MODEL, NETWORK


class SimulationData:
    """
    Contains simulation data and associated functionality.
    """

    DATA_REPO_URL_RAW: Final[str] = DATA_REPO_URL_RAW
    DATA_REPO_SIMULATIONS_PATH: Final[str] = 'simulations'
    DATA_REPO_APP_DATA_PATH: Final[str] = 'app-data'

    MODEL_META = {
        'SEIR': {'compartments': ['S', 'E', 'I', 'R'], 'stem': 'epydemic.SEIR.'},
        'SEIR_Q': {'compartments': ['S', 'E', 'I', 'R'], 'stem': 'epydemic.SEIR.'},
        'SEIVR': {'compartments': ['S', 'E', 'I', 'V', 'R'], 'stem': 'epydemic.SEIVR.'},
        'SEIVR_Q': {'compartments': ['S', 'E', 'I', 'V', 'R'], 'stem': 'epydemic.SEIVR.'},
    }

    COLUMNS = ['experiment_id', 'time', 'compartment', 'value']

    def __init__(self):

        # file info
        self._files = FILES

        # initialise filters
        self._current_state = {}

        # track if files have been loaded yet
        self._files_loaded = False

    @property
    def files(self):
        return self._files

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        assert isinstance(new_state, dict)
        assert 'model' in new_state
        assert 'network' in new_state
        assert 'filters' in new_state
        assert isinstance(new_state['model'], str)
        assert isinstance(new_state['network'], str)
        assert isinstance(new_state['filters'], dict)
        self._current_state = new_state

    @property
    def files_loaded(self):
        return self._files_loaded

    @property
    def models(self):
        return sorted(list(set([x[MODEL] for x in self._files])))

    @property
    def networks(self):
        return sorted(list(set([x[NETWORK] for x in self._files])))

    def load_files(self):
        """
        Load all files from repo.
        :return: Updated files
        """
        pbar = tqdm(self._files)
        for file in pbar:
            self.load_file(file)
            pbar.set_description_str("Loading file %s" % file['name'])

        self._files_loaded = True

    @classmethod
    def load_file(cls, file: Dict) -> Dict:
        """
        Load JSON file from data repo inplace.
        :param file: Dict containing file info, crucially the `name`
        :return: Updated dict including the `content`
        """

        file_name = file['name'] + '.pkl'

        # check if file is available on disk
        local_file = os.path.join(DATA_DIR, file_name)
        if os.path.isfile(local_file):
            with open(local_file, 'rb') as f:
                file['df'] = pickle.load(f)

            return file

        # else, get from data repo
        url = os.path.join(
            cls.DATA_REPO_URL_RAW,
            cls.DATA_REPO_APP_DATA_PATH,
            file_name
        )

        with urlopen(url) as f:
            df = pickle.load(f)
            file['df'] = df

            # ... and save to file for next time
            df.to_pickle(local_file)

        return file

    def subset_data(self, model: str, network: str,
                    filters: Dict) -> pd.DataFrame:
        """
        Return a subset of the data for a `model`, a `network`, and potentially
        filtered by the values specified in `filters`.
        :param model: Model of the subset.
        :param network: Network of the subset.
        :param filters: Dictionary containing columns as keys and filter values
            as values
        :return: The subset as a data frame.
        """

        # make sure files are loaded ...
        assert self._files_loaded

        df = pd.DataFrame()
        found = False
        for file in self._files:
            if file[MODEL] == model and file[NETWORK] == network:
                df = file['df']
                found = True
                break

        if not found:
            raise ValueError(f"Provided combination of `model={model}` and "
                             f"`network={network}` does not exist. "
                             f"The available combinations are "
                             f"{[(x[MODEL], x[NETWORK]) for x in self._files]}.")

        return self._apply_filters(df, filters)

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
    def df_group_mean(df):
        """
        Calculate the mean value per time per compartment.
        :param df: Simulation df.
        :return: grouped data frame.
        """
        grouped = df.groupby(['time', 'compartment']).mean()
        grouped.reset_index(inplace=True)
        return grouped

    @staticmethod
    def epidemic_size_per_param(df, param):
        """
        For the variable parameter `param` calculate the epidemic size
        for each setting and for each experiment in `df`. Return the result
        as a data frame with the columns `param` and 'epidemic_size'
        :param df: Simulation df
        :param param: Target variable parameter
        :return: data frame
        """

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

    @staticmethod
    def calc_perc_infected(df):
        """
        Calculate the percentage of infected individuals from a simulation data
        frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Percentage of infected individuals.
        """
        r = df[df.compartment == 'R'].iloc[0]['value']
        e = df[df.compartment == 'E'].iloc[0]['value']
        return r + e

    @staticmethod
    def calc_susceptible_remaining(df):
        """
        Calculate the percentage of infected individuals from a simulation data
        frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Percentage of susceptible individuals remaining
        """
        susceptible = df[df.compartment == 'S'].iloc[-1]['value']

        if 'V' in df.compartment.values:
            vaccinated = df[df.compartment == 'V'].iloc[-1]['value']
        else:
            vaccinated = 0

        return susceptible + vaccinated

    @staticmethod
    def calc_peak_time(df):
        """
        Calculate the time step of peak infection from a simulation data
        frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Time step of peak infection
        """
        return df.loc[df[df.compartment == 'I'].value.idxmax(), 'time']

    @staticmethod
    def calc_peak_infected(df):
        """
        Calculate the peak infection percentage from a simulation data
        frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Peak infection percentage
        """
        return df[df.compartment == 'I'].value.max()

    @classmethod
    def calc_effective_end(cls, df):
        """
        Calculate the effective end of the epidemic, i.e. when percentage of
        infected individuals is below 1% for the first time from a simulation
        data frame with only one experiment.
        :param df: Simulation data frame with only one experiment
        :return: Time step of effective end
        """
        # first time, infected is sub 1% again
        infected = df[df.compartment == 'I']

        idx = cls.find_sub_threshold_after_peak(infected.value.tolist(), 0.01)

        if idx is None:
            return None

        return infected.time.values[idx]

    @staticmethod
    def find_sub_threshold_after_peak(ls: List, v: float):
        """
        Find the index of the value in a list that is below a threshold  for the
        first time after a value above the peak. If the condition is not met for
        any values, return 0 if the first value of the list is below the threshold
        or None if the first value is above the threshold.
        :param ls: List of values
        :param v: Threshold value
        :return: Index or None
        """
        for i in range(1, len(ls)):
            if ls[i - 1] > v >= ls[i]:
                return i

        return 0 if len(ls) > 0 and ls[0] <= v else None


if __name__ == '__main__':
    test_df = SimulationData.load_file({
        'name': 'seir_plc_pre.json',
        'repo_path': 'simulations',
        MODEL: 'SEIR'
    })
