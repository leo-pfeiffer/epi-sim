import pandas as pd

REPO_URL = "https://github.com/leo-pfeiffer/msc-thesis-data/blob/main"
SEIR_FILE = f"{REPO_URL}/sim_seir.csv"
SEIVR_FILE = f"{REPO_URL}/sim_seivr.csv"

seir_df = pd.read_csv(SEIR_FILE)
seivr_df = pd.read_csv(SEIVR_FILE)