# Script to upload experiment results to data repo.
#  Specify the directory that contains the experiment results (and only those)
#  and upload all to the data repo. The path must be relative to the
#  `experiments` folder. The default directory is `experiment_results`.
#
# This use case works in accordance to the files created in the
#  2_network_creation.ipynb Notebook if the files are not directly uploaded
#  to the repo.
#
# Model experiments are recognised as such if their file name starts with
#  'seir' or 'seivr'. These files will be uploaded to the MODEL_DIR folder in
#  the repo.
#
# All other files in the directory are treated as Network metric experiments
#  and are uploaded to the NETWORK_DIR folder in the repo.

import os
import argparse
from lib.experiments.utils.data_repo_api import DataRepoAPI
from lib.configuration import EXPERIMENTS_DIR

DIR = 'experiment_results'
MODEL_DIR = 'simulations'
NETWORK_DIR = 'network-metrics'


def main(path=DIR):

    path = os.path.join(EXPERIMENTS_DIR, path)

    files = os.listdir(path)

    print(f"Found {len(files)} files to upload")

    for i, file_name in enumerate(files):

        # Skip non-files
        if not os.path.isfile(os.path.join(DIR, file_name)):
            print(f"{i + 1} / {len(files)} : Skipped {file_name} as this is not a file.")
            continue

        # Upload model experiment results
        if file_name.startswith('seir') or file_name.startswith('seivr'):
            DataRepoAPI.update_or_create(file_name=file_name, file_path=DIR, repo_path=MODEL_DIR)

        # Upload network metrics
        else:
            DataRepoAPI.update_or_create(file_name=file_name, file_path=DIR, repo_path=NETWORK_DIR)

        print(f"{i + 1} / {len(files)} : Uploaded file {file_name}")

    print("Done.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='Path relative to experiments folder', required=False)

    args = parser.parse_args()
    target_path = DIR if args.path == '' else DIR
    main(target_path)
