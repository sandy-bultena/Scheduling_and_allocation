# This file is used to declare and use variables that exceed the scope of the individual modules
from typing import Callable

bin_dir: str = None

try:    # if dotenv is installed and a .env file is found, check for a manual bin dir (allows testing from sub-files)
    from dotenv import dotenv_values
    info = dotenv_values()
    bin_dir = info.get('BIN_DIR', None)
except:
    pass

dirty_set: Callable = None
dirty_unset: Callable = None
is_dirty: Callable = None


def set_dirty_flag(*_):
    """Mark as dirty"""
    return dirty_set()


def unset_dirty_flag(*_):
    """Mark as clean"""
    return dirty_unset()


def is_data_dirty():
    """Get the current state of the application, dirty (True) or clean (False)"""
    return is_dirty()


def init_dirty_flag(d_set, unset, check):
    """Set up the view methods that adjust dirty flag"""
    global dirty_set, dirty_unset, is_dirty
    dirty_set = d_set
    dirty_unset = unset
    is_dirty = check
