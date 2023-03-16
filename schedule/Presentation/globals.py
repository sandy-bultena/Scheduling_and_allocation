# This file is used to declare and use variables that exceed the scope of the individual modules

global dirty_ptr


def set_dirty_ptr():
    global dirty_ptr
    dirty_ptr = True


def unset_dirty_ptr():
    global dirty_ptr
    dirty_ptr = False


@property
def is_data_dirty():
    global dirty_ptr
    if dirty_ptr is None: unset_dirty_ptr()
    return dirty_ptr
