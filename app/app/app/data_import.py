import sys
from typing import Dict

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

        self.FILES = FILES

        # load file contents
        self._load_files()

    @property
    def models(self):
        return sorted(list(set([x[MODEL] for x in self.FILES])))

    @property
    def networks(self):
        return sorted(list(set([x[NETWORK] for x in self.FILES])))

    def _load_files(self):
        """
        Load all files from repo.
        :return: Updated files
        """
        pbar = tqdm(self.FILES)
        for file in pbar:
            self.load_file(file)
            pbar.set_description_str("Loading file %s" % file['name'])

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

        df = pd.DataFrame()
        found = False
        for file in self.FILES:
            if file[MODEL] == model and file[NETWORK] == network:
                df = file['df']
                found = True
                break

        if not found:
            raise ValueError(f"Provided combination of `model={model}` and "
                             f"`network={network}` does not exist. "
                             f"The available combinations are "
                             f"{[(x[MODEL], x[NETWORK]) for x in self.FILES]}.")

        # create array with true values only
        arr = np.array([True] * len(df))

        for k, v in filters.items():
            # define filter (taking into account floating point imprecision) and
            #  combine with previous filters
            arr = arr & (lambda x: np.isclose(x, v))(df[k].values)

        return df.loc[arr]


if __name__ == '__main__':
    test_df = SimulationData.load_file({
        'name': 'seir_plc_pre.json',
        'repo_path': 'simulations',
        MODEL: 'SEIR'
    })
