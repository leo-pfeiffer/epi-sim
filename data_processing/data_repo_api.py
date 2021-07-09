import requests
import json
import argparse
import base64
import os
from dotenv import load_dotenv
from configuration import ROOT_DIR, DATA_REPO_URL_API

# load dotenv file and load variables
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, '.env'))

TOKEN = os.getenv("DATA_REPO_TOKEN")

# set auth header
AUTH = {"Authorization": f"token {TOKEN}"}


def update_or_create(file_name, file_path=None):
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

    sha = get_sha(file_name=file_name)
    put_file(file_name, content, sha)


def get_sha(file_name):
    """
    Get the Blob Sha of the file on Github if it exists.
    :param file_name: Name of the file
    :return: SHA or None
    """
    url = f'{DATA_REPO_URL_API}/{file_name}'
    headers = AUTH
    res = requests.get(url, headers=headers)

    if res.status_code == 404:
        return None

    if res.status_code != 200:
        print(res)
        raise requests.exceptions.HTTPError()

    jsn = res.json()
    return jsn['sha']


def put_file(file_name, content, sha=None):
    """
    Perform HTTP Put to create or update the file.
    :param file_name: File name
    :param content: Base 64 encoded string.
    :param sha: Blob SHA of the file (required if update)
    """
    url = f'{DATA_REPO_URL_API}/{file_name}'
    headers = AUTH | {'Accept': 'application/vnd.github.v3+json'}

    data = {
        "message": "file upload",
        "content": content,
    }

    if sha:
        data |= {"sha": sha}

    res = requests.put(url, data=json.dumps(data), headers=headers)

    if not res.ok:
        raise requests.exceptions.HTTPError()


if __name__ == '__main__':
    # if called from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='file name', required=True)

    args = parser.parse_args()
    file = args.file

    update_or_create(file_name=file)
