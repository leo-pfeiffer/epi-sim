import sys
from typing import List, Dict, Any

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

from epydemic import PLCNetwork as PLC
from lib.model.network.mobility_network import MNGeneratorFromNetworkData as MN
from lib.model.network.distanced_network import DNGenerator as DN

from lib.model.compartmental_model.seir import SEIRWithQuarantine
from lib.model.compartmental_model.seivr import SEIVR as SEIVRModel
from lib.model.compartmental_model.seivr import SEIVRWithQuarantine


# Define string constants

# Models
SEIR: Final[str] = 'SEIR'
SEIR_Q: Final[str] = 'SEIR_Q'
SEIVR: Final[str] = 'SEIVR'
SEIVR_Q: Final[str] = 'SEIVR_Q'

# Networks
MN_PRE: Final[str] = 'Mobility (Pre)'
MN_POST: Final[str] = 'Mobility (Post)'
PLC_PRE: Final[str] = 'Power Law Cutoff (Pre)'
PLC_POST: Final[str] = 'Power Law Cutoff (Post)'
DIST_PRE: Final[str] = 'Distanced (Pre)'
DIST_POST: Final[str] = 'Distanced (Post)'

# Keys
MODEL: Final[str] = 'model'
NETWORK: Final[str] = 'network'
NAME: Final[str] = 'name'
COLS: Final[str] = 'columns'

# columns of df

SEIR_Q_COLS = {
    SEIRWithQuarantine.P_QUARANTINE: 'p_quarantine'
}

SEIVR_COLS = {
    SEIVRModel.P_VACCINATED: 'p_vaccinated',
    SEIVRModel.P_VACCINATED_INITIAL: 'p_vaccinated_initial',
    SEIVRModel.VACCINE_RRR: 'rrr'
}

SEIVR_Q_COLS = {
    SEIVRWithQuarantine.P_VACCINATED: 'p_vaccinated',
    SEIVRWithQuarantine.P_VACCINATED_INITIAL: 'p_vaccinated_initial',
    SEIVRWithQuarantine.VACCINE_RRR: 'rrr',
    SEIVRWithQuarantine.P_QUARANTINE: 'p_quarantine'
}

ADD_COLUMN_MAPPING = {
    SEIR: {},
    SEIR_Q: SEIR_Q_COLS,
    SEIVR: SEIVR_COLS,
    SEIVR_Q: SEIVR_Q_COLS
}

# Access parameter size
SIZE_KEY = {
    PLC_PRE: PLC.N,
    PLC_POST: PLC.N,
    MN_PRE: MN.N,
    MN_POST: MN.N,
    DIST_PRE: DN.N,
    DIST_POST: DN.N
}

FILES: List[Dict[str, Any]] = [
    {MODEL: SEIR, NETWORK: MN_PRE, NAME: 'seir_mobility_pre'},
    {MODEL: SEIR, NETWORK: MN_POST, NAME: 'seir_mobility_post'},
    {MODEL: SEIR, NETWORK: PLC_PRE, NAME: 'seir_plc_pre', },
    {MODEL: SEIR, NETWORK: PLC_POST, NAME: 'seir_plc_post'},
    {MODEL: SEIR, NETWORK: DIST_PRE, NAME: 'seir_distanced_pre'},
    {MODEL: SEIR, NETWORK: DIST_POST, NAME: 'seir_distanced_post'},

    {MODEL: SEIR_Q, NETWORK: MN_PRE, NAME: 'seirq_mobility_pre'},
    {MODEL: SEIR_Q, NETWORK: MN_POST, NAME: 'seirq_mobility_post'},
    {MODEL: SEIR_Q, NETWORK: PLC_PRE, NAME: 'seirq_plc_pre'},
    {MODEL: SEIR_Q, NETWORK: PLC_POST, NAME: 'seirq_plc_post'},
    {MODEL: SEIR_Q, NETWORK: DIST_PRE, NAME: 'seirq_distanced_pre'},
    {MODEL: SEIR_Q, NETWORK: DIST_POST, NAME: 'seirq_distanced_post'},

    {MODEL: SEIVR, NETWORK: MN_PRE, NAME: 'seivr_mobility_pre'},
    {MODEL: SEIVR, NETWORK: MN_POST, NAME: 'seivr_mobility_post'},
    {MODEL: SEIVR, NETWORK: PLC_PRE, NAME: 'seivr_plc_pre'},
    {MODEL: SEIVR, NETWORK: PLC_POST, NAME: 'seivr_plc_post'},
    {MODEL: SEIVR, NETWORK: DIST_PRE, NAME: 'seivr_distanced_pre'},
    {MODEL: SEIVR, NETWORK: DIST_POST, NAME: 'seivr_distanced_post'},

    {MODEL: SEIVR_Q, NETWORK: MN_PRE, NAME: 'seivrq_mobility_pre'},
    {MODEL: SEIVR_Q, NETWORK: MN_POST, NAME: 'seivrq_mobility_post'},
    {MODEL: SEIVR_Q, NETWORK: PLC_PRE, NAME: 'seivrq_plc_pre'},
    {MODEL: SEIVR_Q, NETWORK: PLC_POST, NAME: 'seivrq_plc_post'},
    {MODEL: SEIVR_Q, NETWORK: DIST_PRE, NAME: 'seivrq_distanced_pre'},
    {MODEL: SEIVR_Q, NETWORK: DIST_POST, NAME: 'seivrq_distanced_post'},
]