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
from datetime import datetime as dt

from lib.experiments.utils.simulation_files import FILES, SIZE_KEY, \
    ADD_COLUMN_MAPPING
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
PARAMETERS = epyc.Experiment.PARAMETERS

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

    # columns (including additional parameter columns)
    add_columns = ADD_COLUMN_MAPPING[file['model']]
    columns = COLUMNS + list(add_columns.values())

    # data frame in long format
    df = pd.DataFrame(columns=columns)

    for experiment in results:

        # Get parameters
        N = experiment[PARAMETERS][SIZE_KEY[file['network']]]
        experiment_id = experiment[METADATA][EXPERIMENT_ID]
        times = experiment[RESULTS][OBSERVATIONS]

        # number of observations recorded
        num_obs = len(times)

        # for each of the additional parameters of the models, extract the
        #  values and save `num_obs` copies of it in a list to the `add_vals`
        #  list (note: this works in Python 3.6+ thanks to ordered dicts).
        add_vals = []
        for param, col in add_columns.items():
            vals = [experiment[PARAMETERS][param]] * num_obs
            add_vals.append(vals)

        model = MODEL_META[file['model']]
        stem = model['stem']

        # Append the values for each compartment to the long form data frame
        for comp in model['compartments']:
            comp_key = TIMESERIES_STEM + '-' + stem + comp

            # values of current compartment as fraction of population
            values = [x / N for x in experiment[RESULTS][comp_key]]

            # column values for data frame creation
            col_val_list = [
                [experiment_id] * num_obs, times, [comp] * num_obs, values
            ]

            # Map the column value lists (including `add_vals`) to columns
            dic = {
                col: ls for col, ls in zip(columns, col_val_list+add_vals)
           }

            # append this compartment to the data frame
            df = df.append(pd.DataFrame(dic), ignore_index=True)

    print(f"%s loaded file {file['name']}" % dt.now())

    return df


def _pickle_file(file, df):
    """
    Pickle files for upload.
    """

    # make temporary directory
    file_name = os.path.join(TMP_DIR, file['name'] + '.pkl')
    df.to_pickle(file_name)
    print(f"%s pickled file {file['name']}" % dt.now())


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
    print(f"%s uploaded file {file['name']}" % dt.now())


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
