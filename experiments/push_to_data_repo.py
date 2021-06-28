import requests
import json
import argparse
import base64
import os
from dotenv import load_dotenv
from configuration import ROOT_DIR

load_dotenv(dotenv_path=os.path.join(ROOT_DIR, '.env'))

TOKEN = os.getenv("DATA_REPO_TOKEN")
REPO_URL = 'https://api.github.com/repos/leo-pfeiffer/msc-thesis-data/contents'
AUTH = {"Authorization": f"token {TOKEN}"}


def update_or_create(file_name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')

    with open(os.path.join(path, file_name), 'r') as f:
        data = f.read().encode()
        content = base64.b64encode(data).decode()

    sha = get_sha(file_name=file_name)
    put_file(file_name, content, sha)


def get_sha(file_name):
    url = f'{REPO_URL}/{file_name}'
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
    url = f'{REPO_URL}/{file_name}'
    headers = AUTH | {'Accept': 'application/vnd.github.v3+json'}

    data = {
        "message": "file upload",
        "content": content,
    }

    if sha:
        data |= {"sha": sha}

    res = requests.put(url, data=json.dumps(data), headers=headers)

    if not res.ok:
        print(res)
        raise requests.exceptions.HTTPError()


if __name__ == '__main__':
    # if called from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='file name', required=True)

    args = parser.parse_args()
    file = args.file

    update_or_create(file_name=file)
