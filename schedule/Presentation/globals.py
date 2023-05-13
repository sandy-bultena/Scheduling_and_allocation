# This file is used to declare and use variables that exceed the scope of the individual modules
from typing import Callable

dirty_flag = False
bin_dir : str = None
dirty_flag_changed_cb: callable = lambda : None

dirty_set: Callable = None
dirty_unset: Callable = None
is_dirty: Callable = None


def set_dirty_flag(*_):
    """Mark as dirty"""
    global dirty_flag
    dirty_flag = True
    if dirty_flag_changed_cb:
        dirty_flag_changed_cb()


def unset_dirty_flag(*_):
    """Mark as clean"""
    global dirty_flag
    dirty_flag = False
    if dirty_flag_changed_cb:
        dirty_flag_changed_cb()


def is_data_dirty():
    """Get the current state of the application, dirty (True) or clean (False)"""
    return is_dirty()
