# small utility module that contains a function that appends the
# `lib/experiments/` directory to the PYTHONPATH. This is required to allow
# relative imports in the Jupyter notebooks of the directory. To use the
# functions, simply import it and call it at the start of the Notebook.

import os
import sys


def append_sys_path():
    """
    Append project dir to sys path... required to allow relative imports and
     imports from parent package in jupyter notebooks.
    """
    module = os.path.abspath(os.path.join('..'))
    lib = os.path.abspath(os.path.join(module, os.pardir))
    if lib not in sys.path:
        sys.path.append(lib)
