# Batch upload files to the data repository

# todo make this usable from command line


import os
import sys
from lib.experiments.data_repo_api import DataRepoAPI

module = os.path.abspath(os.path.join('..'))
if module not in sys.path:
    sys.path.append(module)

DIR = 'experiment_results'

files = os.listdir(DIR)

print(f"Found {len(files)} files to upload")

for i, file_name in enumerate(files):

    if not os.path.isfile(os.path.join(DIR, file_name)):
        print(f"{i + 1} / {len(files)} : Skipped {file_name} as this is not a file.")
        continue

    if file_name.startswith('seir') or file_name.startswith('seivr'):
        DataRepoAPI.update_or_create(file_name=file_name, file_path=DIR, repo_path='simulations')

    else:
        DataRepoAPI.update_or_create(file_name=file_name, file_path=DIR, repo_path='network-metrics')

    print(f"{i + 1} / {len(files)} : Uploaded file {file_name}")

print("Done.")