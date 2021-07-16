# Global configuration file

import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# load environment variables
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, '../.env'))

# Paths...
DATA = os.path.join(ROOT_DIR, 'data_processing', 'data')
REMOTE_RAW = 'http://209.182.235.76/data/msc/'
RAW = os.path.join(DATA, 'raw/')
OUT = os.path.join(DATA, 'out/')
GRAPHICS = os.path.join(DATA, 'graphics/')
GRAPHS = os.path.join(DATA, 'graphs/')

# Github data repo
DATA_REPO_TOKEN = os.getenv('DATA_REPO_TOKEN')
DATA_REPO_URL_API = os.getenv('DATA_REPO_URL_API')
DATA_REPO_URL_RAW = os.getenv('DATA_REPO_URL_RAW')
DATA_REPO_URL_TREE = os.getenv('DATA_REPO_URL_TREE')