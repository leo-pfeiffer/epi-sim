# Lib configuration file

import os
from dotenv import load_dotenv

LIB_DIR = os.path.dirname(os.path.abspath(__file__))

# load environment variables
load_dotenv(dotenv_path=os.path.join(LIB_DIR, '.env'))

# Paths...
EXPERIMENTS_DIR = os.path.join(LIB_DIR, 'experiments')
DATA = os.path.join(LIB_DIR, 'data_processing', 'data')
REMOTE_RAW = 'http://209.182.235.76/data/msc/'
RAW = None

# Github data repo
DATA_REPO_TOKEN = os.getenv('DATA_REPO_TOKEN')
DATA_REPO_URL_API = os.getenv('DATA_REPO_URL_API')
DATA_REPO_URL_RAW = os.getenv('DATA_REPO_URL_RAW')
DATA_REPO_URL_TREE = os.getenv('DATA_REPO_URL_TREE')
