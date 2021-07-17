import sys
from typing import Callable, Any, Dict

import epyc
import epydemic

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

import pandas as pd
import json
from urllib.request import urlopen
import os

from lib.configuration import DATA_REPO_URL_RAW

EXPERIMENT_ID = epyc.RepeatedExperiment.I
OBSERVATIONS = epydemic.Monitor.OBSERVATIONS
TIMESERIES_STEM = epydemic.Monitor.TIMESERIES_STEM

RESULTSETS = 'resultsets'
RESULTSETS_DEFAULT = epyc.LabNotebook.DEFAULT_RESULTSET
RESULTS = epyc.Experiment.RESULTS
METADATA = epyc.Experiment.METADATA


class SimulationData:
    """
    Contains simulation data and associated functionality.
    """

    DATA_REPO_URL_RAW: Final[str] = DATA_REPO_URL_RAW
    DATA_REPO_SIMULATIONS_PATH: Final[str] = 'simulations'

    MODEL_META = {
        'SEIR': {'compartments': ['S', 'E', 'I', 'R'], 'stem': 'epydemic.SEIR.'},
        'SEIR_Q': {'compartments': ['S', 'E', 'I', 'R'], 'stem': 'epydemic.SEIR.'},
        'SEIVR': {'compartments': ['S', 'E', 'I', 'V', 'R'], 'stem': 'epydemic.SEIVR.'},
        'SEIVR_Q': {'compartments': ['S', 'E', 'I', 'V', 'R'], 'stem': 'epydemic.SEIVR.'},
    }

    COLUMNS = ['experiment_id', 'time', 'compartment', 'value']

    def __init__(self):

        self.FILES = [
            {'model': 'SEIR', 'network': 'MN_Pre', 'name': 'sim_seir.json'},
            # todo add all files (24 in total)
        ]

        # load file contents
        # todo change to new version
        self._load_files()
        # self._load_file_old()

    @property
    def models(self):
        return sorted(list(set([x['model'] for x in self.FILES])))

    @property
    def networks(self):
        return sorted(list(set([x['network'] for x in self.FILES])))

    def _load_files(self):
        """
        Load all files from repo.
        :return: Updated files
        """
        for file in self.FILES:
            self.load_file(file)

    @classmethod
    def load_file(cls, file: Dict) -> Dict:
        """
        Load JSON file from data repo inplace.
        :param file: Dict containing file info, crucially the `name`
        :return: Updated dict including the `content`
        """
        url = os.path.join(
            cls.DATA_REPO_URL_RAW,
            cls.DATA_REPO_SIMULATIONS_PATH,
            file['name']
        )

        with urlopen(url) as f:
            content = json.load(f)

        results = content[RESULTSETS][RESULTSETS_DEFAULT][RESULTS]

        df = pd.DataFrame(
            columns=cls.COLUMNS
        )

        for experiment in results:

            experiment_id = experiment[METADATA][EXPERIMENT_ID]
            times = experiment[RESULTS][OBSERVATIONS]

            num_obs = len(times)

            model = cls.MODEL_META[file['model']]
            stem = model['stem']

            for comp in model['compartments']:
                comp_key = TIMESERIES_STEM + '-' + stem + comp
                values = experiment[RESULTS][comp_key]

                dic = {col: ls for col, ls in zip(cls.COLUMNS, [
                    [experiment_id] * num_obs, times,
                    [comp] * num_obs, values])
               }

                df = df.append(pd.DataFrame(dic), ignore_index=True)

        file['df'] = df

        return df

    @staticmethod
    def make_filter_func(filters: Dict[str, Any]) -> Callable:
        """
        Make a filter function from a dictionary of filter.
         For example, to filter for `compartment == 'susceptible`, pass
         `filters = {'compartment' : 'susceptible'}`.
        :param filters: Dictionary of filter criteria
        :return: Callable to use for filtering
        """

        # base case: always return True
        func: Callable = lambda x: True

        # consider all filter conditions
        for k, v in filters.items():
            # new filter condition as a function
            new_func: Callable = lambda x: x[k] == v
            # combine new and old filter with AND
            func: Callable = lambda x: func(x) & new_func(x)

        return func

    def subset_data(self, model: str, network: str,
                    apply_func: Callable = lambda x: True) -> pd.DataFrame:
        """
        Return a subset of the data for a `model`, a `network`, and potentially
        filtered by an apply function.
        :param model: Model of the subset.
        :param network: Network of the subset.
        :param apply_func: Function to filter with.
        :return: The subset as a data frame.
        """

        df = pd.DataFrame()
        found = False
        for file in self.FILES:
            if file['model'] == model and file['network'] == network:
                df = file['content']
                found = True
                break

        if not found:
            raise ValueError(f"Provided combination of `model={model}` and "
                             f"`network={network}` does not exist. "
                             f"The available combinations are "
                             f"{[(x['model'], x['network']) for x in self.FILES]}.")

        subset = df[df.apply(apply_func, 1)].copy()

        return subset

    def _load_file_old(self):
        seir_file = f"{self.DATA_REPO_URL_RAW}/sim_seir.csv"
        seivr_file = f"{self.DATA_REPO_URL_RAW}/sim_seivr.csv"

        seir_df = pd.read_csv(seir_file, index_col=0)
        seir_q_df = seir_df[seir_df.model == 'SEIR_Q']
        seir_df = seir_df[seir_df.model == 'SEIR']

        seivr_df = pd.read_csv(seivr_file, index_col=0)
        seivr_q_df = seivr_df[seivr_df.model == 'SEIVR_Q']
        seivr_df = seivr_df[seivr_df.model == 'SEIVR']

        self.FILES = []

        # SEIR
        for network in seir_df.network.unique().tolist():
            self.FILES.append({
                'model': 'SEIR',
                'network': network,
                'content': seir_df[seir_df.network == network]
            })

        # SEIR_Q
        for network in seir_q_df.network.unique().tolist():
            self.FILES.append({
                'model': 'SEIR_Q',
                'network': network,
                'content': seir_q_df[seir_q_df.network == network]
            })

        # SEIVR
        for network in seivr_df.network.unique().tolist():
            self.FILES.append({
                'model': 'SEIVR',
                'network': network,
                'content': seivr_df[seivr_df.network == network]
            })

        # SEIVR_Q
        for network in seivr_q_df.network.unique().tolist():
            self.FILES.append({
                'model': 'SEIVR_Q',
                'network': network,
                'content': seir_df[seir_df.network == network]
            })


simulation_data = SimulationData()


if __name__ == '__main__':
    test_df = SimulationData.load_file({
        'name': 'seir_plc_pre.json',
        'repo_path': 'simulations',
        'model': 'SEIR'
    })
