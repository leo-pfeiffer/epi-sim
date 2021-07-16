# Configuration file for Web app

import os
from dotenv import load_dotenv

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# load environment variables from  .env file
load_dotenv(dotenv_path=os.path.join(PARENT_DIR, '.env'))

DATA_REPO_URL_RAW = os.getenv('DATA_REPO_URL_RAW')
