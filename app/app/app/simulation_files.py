# Contains information about the simulation files.

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
DISEASE: Final[str] = 'disease'

# Disease names
D_COVID = 'COVID-19'
D_INFLUENZA = 'Influenza'

# Parameter mapping
ID_P_QUAR: Final[str] = 'p_quarantine'
ID_P_VACC: Final[str] = 'p_vaccinated'
ID_P_VACC_INIT: Final[str] = 'p_vaccinated_initial'
ID_RRR: Final[str] = 'rrr'

# Values
VALS_MAPPING = {
    ID_P_QUAR: {'min': 0, 'max': 1, 'step': 0.25},
    ID_P_VACC: {'min': 0.001, 'max': 0.01, 'step': 0.003},
    ID_P_VACC_INIT: {'min': 0, 'max': 0.8, 'step': 0.2},
    ID_RRR: {'min': 0.5, 'max': 0.95, 'step': 0.15},
}

PARAM_MAPPING = {
    SEIR: {ID_P_QUAR: False, ID_P_VACC: False, ID_P_VACC_INIT: False, ID_RRR: False},
    SEIR_Q: {ID_P_QUAR: True, ID_P_VACC: False, ID_P_VACC_INIT: False, ID_RRR: False},
    SEIVR: {ID_P_QUAR: False, ID_P_VACC: True, ID_P_VACC_INIT: True, ID_RRR: True},
    SEIVR_Q: {ID_P_QUAR: True, ID_P_VACC: True, ID_P_VACC_INIT: True, ID_RRR: True},
}

NETWORK_MAPPING = {
    D_COVID: [MN_PRE, MN_POST, PLC_PRE, PLC_POST, DIST_PRE, DIST_POST],
    D_INFLUENZA: [MN_PRE, MN_POST]
}

MODELS: List[str] = [SEIR, SEIR_Q, SEIVR, SEIVR_Q]
NETWORKS: List[str] = [MN_PRE, MN_POST, PLC_PRE, PLC_POST, DIST_PRE, DIST_POST]
DISEASES = [D_COVID, D_INFLUENZA]

FILES: List[Dict[str, Any]] = [
    {DISEASE: D_COVID, MODEL: SEIR, NETWORK: MN_PRE, NAME: 'seir_mobility_pre'},
    {DISEASE: D_COVID, MODEL: SEIR, NETWORK: MN_POST, NAME: 'seir_mobility_post'},
    {DISEASE: D_COVID, MODEL: SEIR, NETWORK: PLC_PRE, NAME: 'seir_plc_pre'},
    {DISEASE: D_COVID, MODEL: SEIR, NETWORK: PLC_POST, NAME: 'seir_plc_post'},
    {DISEASE: D_COVID, MODEL: SEIR, NETWORK: DIST_PRE, NAME: 'seir_distanced_pre'},
    {DISEASE: D_COVID, MODEL: SEIR, NETWORK: DIST_POST, NAME: 'seir_distanced_post'},

    {DISEASE: D_COVID, MODEL: SEIR_Q, NETWORK: MN_PRE, NAME: 'seirq_mobility_pre'},
    {DISEASE: D_COVID, MODEL: SEIR_Q, NETWORK: MN_POST, NAME: 'seirq_mobility_post'},
    {DISEASE: D_COVID, MODEL: SEIR_Q, NETWORK: PLC_PRE, NAME: 'seirq_plc_pre'},
    {DISEASE: D_COVID, MODEL: SEIR_Q, NETWORK: PLC_POST, NAME: 'seirq_plc_post'},
    {DISEASE: D_COVID, MODEL: SEIR_Q, NETWORK: DIST_PRE, NAME: 'seirq_distanced_pre'},
    {DISEASE: D_COVID, MODEL: SEIR_Q, NETWORK: DIST_POST, NAME: 'seirq_distanced_post'},

    {DISEASE: D_COVID, MODEL: SEIVR, NETWORK: MN_PRE, NAME: 'seivr_mobility_pre'},
    {DISEASE: D_COVID, MODEL: SEIVR, NETWORK: MN_POST, NAME: 'seivr_mobility_post'},
    {DISEASE: D_COVID, MODEL: SEIVR, NETWORK: PLC_PRE, NAME: 'seivr_plc_pre'},
    {DISEASE: D_COVID, MODEL: SEIVR, NETWORK: PLC_POST, NAME: 'seivr_plc_post'},
    {DISEASE: D_COVID, MODEL: SEIVR, NETWORK: DIST_PRE, NAME: 'seivr_distanced_pre'},
    {DISEASE: D_COVID, MODEL: SEIVR, NETWORK: DIST_POST, NAME: 'seivr_distanced_post'},

    {DISEASE: D_COVID, MODEL: SEIVR_Q, NETWORK: MN_PRE, NAME: 'seivrq_mobility_pre'},
    {DISEASE: D_COVID, MODEL: SEIVR_Q, NETWORK: MN_POST, NAME: 'seivrq_mobility_post'},
    {DISEASE: D_COVID, MODEL: SEIVR_Q, NETWORK: PLC_PRE, NAME: 'seivrq_plc_pre'},
    {DISEASE: D_COVID, MODEL: SEIVR_Q, NETWORK: PLC_POST, NAME: 'seivrq_plc_post'},
    {DISEASE: D_COVID, MODEL: SEIVR_Q, NETWORK: DIST_PRE, NAME: 'seivrq_distanced_pre'},
    {DISEASE: D_COVID, MODEL: SEIVR_Q, NETWORK: DIST_POST, NAME: 'seivrq_distanced_post'},

    {DISEASE: D_INFLUENZA, MODEL: SEIR, NETWORK: MN_PRE, NAME: 'influenza_seir_mobility_pre'},
    {DISEASE: D_INFLUENZA, MODEL: SEIR, NETWORK: MN_POST, NAME: 'influenza_seir_mobility_post'},

    {DISEASE: D_INFLUENZA, MODEL: SEIR_Q, NETWORK: MN_PRE, NAME: 'influenza_seirq_mobility_pre'},
    {DISEASE: D_INFLUENZA, MODEL: SEIR_Q, NETWORK: MN_POST, NAME: 'influenza_seirq_mobility_post'},

    {DISEASE: D_INFLUENZA, MODEL: SEIVR, NETWORK: MN_PRE, NAME: 'influenza_seivr_mobility_pre'},
    {DISEASE: D_INFLUENZA, MODEL: SEIVR, NETWORK: MN_POST, NAME: 'influenza_seivr_mobility_post'},

    {DISEASE: D_INFLUENZA, MODEL: SEIVR_Q, NETWORK: MN_PRE, NAME: 'influenza_seivrq_mobility_pre'},
    {DISEASE: D_INFLUENZA, MODEL: SEIVR_Q, NETWORK: MN_POST, NAME: 'influenza_seivrq_mobility_post'},
]