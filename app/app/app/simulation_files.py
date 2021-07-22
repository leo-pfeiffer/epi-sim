# Contains information about the simulation files. This duplicates some of the
# code defined in `lib`, however since `app` and `lib` are supposed to be usable
# independently of each other, I could not think of an elegant way to avoid
# this. Considering that one could use different data sets in `app` than were
# produced in `lib`, this could come in handy, though.

import sys
from typing import List, Dict, Any

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

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

# Parameter mapping
ID_P_QUAR: Final[str] = 'p_quarantine'
ID_P_VACC: Final[str] = 'p_vaccinated'
ID_P_VACC_INIT: Final[str] = 'p_vaccinated_initial'
ID_RRR: Final[str] = 'rrr'

# Values
VALS_MAPPING = {
    ID_P_QUAR: {'min': 0, 'max': 1, 'step': 0.25},
    ID_P_VACC: {'min': 0.001, 'max': 0.01, 'step': 0.003},
    ID_P_VACC_INIT: {'min': 0, 'max': 1, 'step': 0.2},
    ID_RRR: {'min': 0.5, 'max': 0.95, 'step': 0.15},
}

PARAM_MAPPING = {
    SEIR: {ID_P_QUAR: False, ID_P_VACC: False, ID_P_VACC_INIT: False, ID_RRR: False},
    SEIR_Q: {ID_P_QUAR: True, ID_P_VACC: False, ID_P_VACC_INIT: False, ID_RRR: False},
    SEIVR: {ID_P_QUAR: False, ID_P_VACC: True, ID_P_VACC_INIT: True, ID_RRR: True},
    SEIVR_Q: {ID_P_QUAR: True, ID_P_VACC: True, ID_P_VACC_INIT: True, ID_RRR: True},
}

MODELS: List[str] = [SEIR, SEIR_Q, SEIVR, SEIVR_Q]
NETWORKS: List[str] = [MN_PRE, MN_POST, PLC_PRE, PLC_POST, DIST_PRE, DIST_POST]

FILES: List[Dict[str, Any]] = [
    {MODEL: SEIR, NETWORK: MN_PRE, NAME: 'seir_mobility_pre'},
    {MODEL: SEIR, NETWORK: MN_POST, NAME: 'seir_mobility_post'},
    {MODEL: SEIR, NETWORK: PLC_PRE, NAME: 'seir_plc_pre'},
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
