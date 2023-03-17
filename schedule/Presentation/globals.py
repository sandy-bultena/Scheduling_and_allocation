# This file is used to declare and use variables that exceed the scope of the individual modules

global dirty_flag


def set_dirty_flag():
    global dirty_flag
    dirty_flag = True


def unset_dirty_flag():
    global dirty_flag
    dirty_flag = False


@property
def is_data_dirty():
    global dirty_flag
    if dirty_flag is None: unset_dirty_flag()
    return dirty_flag
