import os
module = os.path.abspath(os.path.join('..'))

DATA = os.path.join(module, 'data_processing', 'data/')
REMOTE_RAW = 'http://209.182.235.76/data/msc/'
RAW = os.path.join(DATA, 'raw/')
OUT = os.path.join(DATA, 'out/')
GRAPHICS = os.path.join(DATA, 'graphics/')
GRAPHS = os.path.join(DATA, 'graphs/')
