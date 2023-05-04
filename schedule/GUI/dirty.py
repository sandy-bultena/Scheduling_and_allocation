# COMPLETED
"""Contains the dirty flag"""
from tkinter import BooleanVar

dirty_flag: BooleanVar

# try to init dirty_flag
# depending on the order files are imported, may fail, in which case leave it for later
try:
    dirty_flag = BooleanVar(value=False)
except:
    pass


def set_(*_):
    """Mark as dirty"""
    init_dirty_flag(True)
    dirty_flag.set(True)


def unset(*_):
    """Mark as clean"""
    init_dirty_flag()
    dirty_flag.set(False)


def check():
    """Get the current state of the application, dirty (True) or clean (False)"""
    global dirty_flag
    init_dirty_flag()
    return dirty_flag.get()


def init_dirty_flag(default=False):
    """Initialize the dirty tracker, if it isn't already"""
    global dirty_flag
    try:
        if dirty_flag is None:
            dirty_flag = BooleanVar(value=default)
    except NameError:
        dirty_flag = BooleanVar(value=default)  # if undefined
