# test imports in app
from ..configuration import *
from ..layouts import *
from ..log_config import *
from ..mixins import *
from ..simulation_files import *
from ..static_elements import *
from ..pages.about import *
from ..pages.models import *
from ..pages.networks import *
from ..pages.not_found import *

# Note: can't import:
#   - data_processing
#   - server
#   - pages.index
#   - pages.validation
# since this would trigger the downloads


def test_imports():
    # only need to call this method, don't need to do anything
    pass
