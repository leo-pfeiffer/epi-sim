# test imports in app
from ..configuration import *
from ..layouts import *
from ..log_config import *
from ..mixins import *
from ..simulation_files import *
from ..static_elements import *

# Note: can't import:
#   - data_processing
#   - server
#   - pages
# since this would trigger the downloads


def test_imports():
    # only need to call this method, don't need to do anything
    pass
