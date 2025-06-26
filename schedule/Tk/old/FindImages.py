import re, platform
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
from schedule.presenter import dirty_flags


def get_image_dir():
    """Gets the image directory"""
    return os.path.join(dir_path, 'Images')


def get_logo():
    return os.path.join(globals.bin_dir, 'ScheduleLogo.gif')


def get_allocation_logo():
    return os.path.join(globals.bin_dir, 'AllocationLogo.gif')
