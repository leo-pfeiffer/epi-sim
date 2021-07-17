# Script to transform all simulation result files to pandas DataFrame for use
#  in the web application. Data frames are pickled and uploaded to the data
#  repo.
#
# All files specified in lib/experiments/scripts/simulation_files are included.

import sys
if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

from typing import Dict

import os
import shutil
import epyc
import epydemic
import time
from urllib.request import urlopen
import json
import pandas as pd

from lib.experiments.utils.simulation_files import FILES
from lib.configuration import DATA_REPO_URL_RAW
from lib.experiments.utils.data_repo_api import DataRepoAPI

# temporary directory
TMP_DIR = 'tmp' + str(int(time.time()))

# String constants
EXPERIMENT_ID = epyc.RepeatedExperiment.I
OBSERVATIONS = epydemic.Monitor.OBSERVATIONS
TIMESERIES_STEM = epydemic.Monitor.TIMESERIES_STEM

RESULTSETS = 'resultsets'
RESULTSETS_DEFAULT = epyc.LabNotebook.DEFAULT_RESULTSET
RESULTS = epyc.Experiment.RESULTS
METADATA = epyc.Experiment.METADATA

# Repo directories
DATA_REPO_SIMULATIONS_PATH: Final[str] = 'simulations'
DATA_REPO_APP_DATA_PATH: Final[str] = 'app-data'

MODEL_META = {
    'SEIR': {'compartments': ['S', 'E', 'I', 'R'], 'stem': 'epydemic.SEIR.'},
    'SEIR_Q': {'compartments': ['S', 'E', 'I', 'R'], 'stem': 'epydemic.SEIR.'},
    'SEIVR': {'compartments': ['S', 'E', 'I', 'V', 'R'], 'stem': 'epydemic.SEIVR.'},
    'SEIVR_Q': {'compartments': ['S', 'E', 'I', 'V', 'R'], 'stem': 'epydemic.SEIVR.'},
}

COLUMNS = ['experiment_id', 'time', 'compartment', 'value']


def _load_file(file: Dict):
    """
    Load JSON file from data repo inplace.
    :param file: Dict containing file info, crucially the `name`
    :return: Updated dict including the `content`
    """
    url = os.path.join(
        DATA_REPO_URL_RAW,
        DATA_REPO_SIMULATIONS_PATH,
        file['name'] + '.json'
    )

    with urlopen(url) as f:
        content = json.load(f)

    results = content[RESULTSETS][RESULTSETS_DEFAULT][RESULTS]

    df = pd.DataFrame(columns=COLUMNS)

    for experiment in results:

        experiment_id = experiment[METADATA][EXPERIMENT_ID]
        times = experiment[RESULTS][OBSERVATIONS]

        num_obs = len(times)

        model = MODEL_META[file['model']]
        stem = model['stem']

        for comp in model['compartments']:
            comp_key = TIMESERIES_STEM + '-' + stem + comp
            values = experiment[RESULTS][comp_key]

            dic = {
                col: ls for col, ls in zip(COLUMNS, [
                    [experiment_id] * num_obs, times,
                    [comp] * num_obs, values])
           }

            df = df.append(pd.DataFrame(dic), ignore_index=True)

    print(f"loaded file {file['name']}")

    return df


def _pickle_file(file, df):
    """
    Pickle files for upload.
    """

    # make temporary directory
    file_name = os.path.join(TMP_DIR, file['name'] + '.pkl')
    df.to_pickle(file_name)
    print(f"pickled file {file['name']}")


def _upload_file(file):
    """
    Upload pickled files.
    """

    file_name = file['name'] + '.pkl'
    repo_path = DATA_REPO_APP_DATA_PATH
    DataRepoAPI.update_or_create(
        file_name=file_name,
        file_path=TMP_DIR,
        repo_path=repo_path
    )
    print(f"uploaded file {file['name']}")


def main():
    """
    Run the process.
    """

    # make temporary directory
    os.mkdir(TMP_DIR)

    try:
        for file in FILES:
            df = _load_file(file)
            _pickle_file(file, df)
            _upload_file(file)

    finally:
        # remove temporary directory
        shutil.rmtree(TMP_DIR)


if __name__ == '__main__':
    main()
