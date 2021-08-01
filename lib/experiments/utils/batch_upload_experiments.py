# Script to upload experiment results to data repo. The script assumes that
#  the experimental results are in the `lib/experiments/experiment_results`
#  directory.
#
# This use case works in accordance to the files created in the
#  2_create_and_simulate.ipynb Notebook if the files are not directly uploaded
#  to the repo (which should usually be the case, though)
#
# Model experiments are recognised as such if their file name starts with
#  'seir' or 'seivr'. These files will be uploaded to the MODEL_DIR folder in
#  the repo.
#
# All other files in the directory are treated as Network metric experiments
#  and are uploaded to the NETWORK_DIR folder in the repo.

import os
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
            print(f"{i + 1} / {len(files)} : "
                  f"Skipped {file_name} as this is not a file.")
            continue

        # Upload model experiment results
        if file_name.startswith('seir') or file_name.startswith('seivr'):
            DataRepoAPI.update_or_create(
                file_name=file_name, file_path=DIR, repo_path=MODEL_DIR
            )

        # Upload network metrics
        else:
            DataRepoAPI.update_or_create(
                file_name=file_name, file_path=DIR, repo_path=NETWORK_DIR
            )

        print(f"{i + 1} / {len(files)} : Uploaded file {file_name}")

    print("Done.")


if __name__ == '__main__':
    main()
