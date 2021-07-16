# Configuration file for Web app

import os
from dotenv import load_dotenv

APP_DIR = os.path.dirname(os.path.abspath(__file__))

os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(APP_DIR, 'app.env'))

DATA_REPO_URL_RAW = os.getenv('DATA_REPO_URL_RAW')
