import pickle
import urllib
import requests
import json
import argparse
import base64
import os
from lib.configuration import DATA_REPO_URL_API, DATA_REPO_URL_TREE, \
    DATA_REPO_URL_RAW, DATA_REPO_TOKEN


class DataRepoAPI:
    """
    Simple wrapper around the Github API to interact with the data repository.
    """

    AUTH = {"Authorization": f"token {DATA_REPO_TOKEN}"}
    CONTENT_TYPE = 'application/vnd.github.v3+json'
    DEFAULT_FILE_DIR = '../experiments/results'

    @classmethod
    def update_or_create(cls, file_name, file_path=None, repo_path=None):
        """
        Update or create the file in the data repo on github.
        :param file_name: Name of the file
        :param file_path: (optional) Path to the file
        :param repo_path: (optional) Path to the file in the repository.
        """
        if file_path is None:
            file_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), cls.DEFAULT_FILE_DIR
            )

        with open(os.path.join(file_path, file_name), 'rb') as f:
            data = f.read()
            content = base64.b64encode(data).decode()

        sha = cls.get_sha(file_name=file_name, repo_path=repo_path)
        cls.put_file(file_name, content, repo_path, sha)

    @classmethod
    def get_tree(cls, tree_url, target):
        res = requests.get(tree_url, headers=cls.AUTH)
        if res.status_code != 200:
            print(res, res.text)
            raise requests.exceptions.HTTPError()

        jsn = res.json()
        e = [x for x in jsn['tree'] if x['path'] == target]

        if len(e) == 0:
            return None, None

        return e[0]['sha'], e[0]['url']

    @classmethod
    def get_sha(cls, file_name, repo_path=None):
        """
        Get the Blob Sha of the file on Github if it exists.
        :param file_name: Name of the file
        :param repo_path: (optional) Path to the file in the repository.
        :return: SHA or None
        """

        if repo_path:
            _, url = cls.get_tree(DATA_REPO_URL_TREE, repo_path)
        else:
            url = DATA_REPO_URL_TREE

        if not url:
            return None

        sha, _ = cls.get_tree(url, file_name)

        return sha

    @classmethod
    def put_file(cls, file_name, content, repo_path=None, sha=None):
        """
        Perform HTTP Put to create or update the file.
        :param file_name: File name
        :param content: Base 64 encoded string.
        :param repo_path: (optional) Path to the file in the repository.
        :param sha: Blob SHA of the file (required if update)
        """

        if not repo_path:
            repo_path = ''

        url = os.path.join(DATA_REPO_URL_API, repo_path, file_name)
        headers = {**cls.AUTH, 'Accept': cls.CONTENT_TYPE}

        data = {
            "message": "file upload",
            "content": content,
        }

        if sha:
            data = {**data, "sha": sha}

        res = requests.put(url, data=json.dumps(data), headers=headers)

        if not res.ok:
            raise requests.exceptions.HTTPError()

    @classmethod
    def get_pickle_file(cls, file_name):
        """
        Get a Pickle file from the data repo.
        :param file_name: Name of the file.
        :return: The file.
        """
        with urllib.request.urlopen(f"{DATA_REPO_URL_RAW}/{file_name}") as url:
            data = pickle.load(url)

        return data

    @classmethod
    def get_json_file(cls, file_name):
        """
        Get a JSON file from the data repo.
        :param file_name: Name of the file.
        :return: The file.
        """
        with urllib.request.urlopen(f"{DATA_REPO_URL_RAW}/{file_name}") as url:
            data = json.load(url)

        return data


if __name__ == '__main__':
    # if called from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name', type=str, help='file name', required=True)
    parser.add_argument('--file_path', type=str, help='file path', required=False)
    parser.add_argument('--repo_path', type=str, help='repo path', required=False)

    args = parser.parse_args()
    name = args.file_name
    path = None if args.file_path == '' else args.file_path
    r_path = None if args.repo_path == '' else args.repo_path

    DataRepoAPI.update_or_create(name, path, r_path)
