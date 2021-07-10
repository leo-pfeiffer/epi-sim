import pickle
import urllib

import requests
import json
import argparse
import base64
import os
from dotenv import load_dotenv
from configuration import ROOT_DIR, DATA_REPO_URL_API, DATA_REPO_URL_TREE, DATA_REPO_URL_RAW

# load dotenv file and load variables
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, '.env'))


class DataRepoAPI:

    TOKEN = os.getenv("DATA_REPO_TOKEN")
    AUTH = {"Authorization": f"token {TOKEN}"}

    @classmethod
    def update_or_create(cls, file_name, file_path=None):
        """
        Update or create the file in the data repo on github.
        :param file_name: Name of the file
        :param file_path: (optional) Path to the file
        """
        if file_path is None:
            file_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), '../experiments/results'
            )

        with open(os.path.join(file_path, file_name), 'rb') as f:
            data = f.read()
            content = base64.b64encode(data).decode()

        sha = cls.get_sha(file_name=file_name)
        cls.put_file(file_name, content, sha)

    @classmethod
    def get_sha(cls, file_name):
        """
        Get the Blob Sha of the file on Github if it exists.
        :param file_name: Name of the file
        :return: SHA or None
        """
        res = requests.get(DATA_REPO_URL_TREE, headers=cls.AUTH)

        if res.status_code != 200:
            print(res, res.text)
            raise requests.exceptions.HTTPError()

        jsn = res.json()
        e = [x for x in jsn['tree'] if x['path'] == file_name]

        if len(e) == 0:
            return None

        else:
            return e[0]['sha']

    @classmethod
    def put_file(cls, file_name, content, sha=None):
        """
        Perform HTTP Put to create or update the file.
        :param file_name: File name
        :param content: Base 64 encoded string.
        :param sha: Blob SHA of the file (required if update)
        """
        url = f'{DATA_REPO_URL_API}/{file_name}'
        headers = cls.AUTH | {'Accept': 'application/vnd.github.v3+json'}

        data = {
            "message": "file upload",
            "content": content,
        }

        if sha:
            data |= {"sha": sha}

        res = requests.put(url, data=json.dumps(data), headers=headers)

        if not res.ok:
            raise requests.exceptions.HTTPError()

    @classmethod
    def get_pickle_file(cls, file_name):
        with urllib.request.urlopen(f"{DATA_REPO_URL_RAW}/{file_name}") as url:
            data = pickle.load(url)

        return data

    @classmethod
    def get_json_file(cls, file_name):
        with urllib.request.urlopen(f"{DATA_REPO_URL_RAW}/{file_name}") as url:
            data = json.load(url)

        return data


if __name__ == '__main__':
    # if called from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='file name', required=True)

    args = parser.parse_args()
    file = args.file

    DataRepoAPI.update_or_create(file_name=file)
