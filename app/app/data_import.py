import pandas as pd

REPO_URL = "https://raw.githubusercontent.com/leo-pfeiffer/msc-thesis-data/main"
SEIR_FILE = f"{REPO_URL}/sim_seir.csv"
SEIVR_FILE = f"{REPO_URL}/sim_seivr.csv"

# seir_df = pd.read_csv(SEIR_FILE, index_col=0)
seir_df = pd.DataFrame()
seivr_df = pd.read_csv(SEIVR_FILE, index_col=0)
