import os

# Paths...
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT_DIR, 'data_processing', 'data')
REMOTE_RAW = 'http://209.182.235.76/data/msc/'
RAW = os.path.join(DATA, 'raw/')
OUT = os.path.join(DATA, 'out/')
GRAPHICS = os.path.join(DATA, 'graphics/')
GRAPHS = os.path.join(DATA, 'graphs/')

# Github
DATA_REPO_URL_API = "https://api.github.com/repos/leo-pfeiffer/msc-thesis-data/contents"

# "/repos/leo-pfeiffer/msc-thesis-data/git/blobs/{file_sha}"

DATA_REPO_URL_RAW = "https://raw.githubusercontent.com/leo-pfeiffer/msc-thesis-data/main"
DATA_REPO_URL_TREE = "https://api.github.com/repos/leo-pfeiffer/msc-thesis-data/git/trees/main"