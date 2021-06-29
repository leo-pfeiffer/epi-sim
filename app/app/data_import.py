import pandas as pd

REPO_URL = "https://raw.githubusercontent.com/leo-pfeiffer/msc-thesis-data/main"
SEIR_FILE = f"{REPO_URL}/sim_seir.csv"
SEIVR_FILE = f"{REPO_URL}/sim_seivr.csv"


def get_files():
    seir_df = pd.read_csv(SEIR_FILE, index_col=0)
    seivr_df = pd.read_csv(SEIVR_FILE, index_col=0)

    return dict(
        seir=dict(
            model='SEIR',
            df=seir_df[seir_df.model == 'SEIR'],
            networks=seir_df[seir_df.model == 'SEIR'].network.unique().tolist()
        ),
        seir_q=dict(
            model='SEIR_Q',
            df=seir_df[seir_df.model == 'SEIR_Q'],
            networks=seir_df[seir_df.model == 'SEIR_Q'].network.unique().tolist()
        ),
        seivr=dict(
            model='SEIVR',
            df=seivr_df[seivr_df.model == 'SEIVR'],
            networks=seivr_df[seivr_df.model == 'SEIVR'].network.unique().tolist()
        ),
        seivr_q=dict(
            model='SEIVR_Q',
            df=seivr_df[seivr_df.model == 'SEIVR_Q'],
            networks=seivr_df[seivr_df.model == 'SEIVR_Q'].network.unique().tolist()
        )
    )


data = get_files()
