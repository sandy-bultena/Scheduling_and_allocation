# # This file is used to declare and use variables that exceed the scope of the individual modules
# from typing import Callable
# import os
#
# # TODO: there seems to some unused methods (dirty_set, dirty_unset, is_dirty)
#
# dirty_flag = False
# dirty_flag_changed_cb: callable = lambda *_: None
#
# dirty_set: Callable = lambda *_: None
# dirty_unset: Callable = lambda *_: None
#
#
# def set_dirty_flag(*_):
#     """Mark as dirty"""
#     global dirty_flag
#     dirty_flag = True
#     dirty_flag_changed_cb()
#
#
# def unset_dirty_flag(*_):
#     """Mark as clean"""
#     global dirty_flag
#     dirty_flag = False
#     dirty_flag_changed_cb()
#
#
# # TODO: Not sure if we need this
# def is_data_dirty():
#     """Get the current state of the application, dirty (True) or clean (False)"""
#     return dirty_flag
