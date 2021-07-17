# Basic file utils

import pickle
import os


def load_pickle_from_disk(dirname, file_name):
    """
    Load a pickled file from disk.
    :param dirname: Name of the directory of the file.
    :param file_name: Name of the file.
    :return: Python object.
    """
    return pickle.load(open(os.path.join(dirname, file_name), 'rb'))
