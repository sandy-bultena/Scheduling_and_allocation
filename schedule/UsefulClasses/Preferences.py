from __future__ import annotations
import configparser as cp
import os
import platform
import re
from typing import *

valid_semester = Literal['fall', 'summer', 'winter']


class Preferences:
    def __init__(self):
        self._config: cp.ConfigParser = _read_ini()

    def home_directory(self):
        operating_system = platform.system().lower()

        user_base_dir = None
        if re.search(r'win', operating_system):
            user_base_dir = os.environ['CSIDL_MYDOCUMENTS'] if os.environ['CSIDL_MYDOCUMENTS'] else None
        elif re.search('darwin', operating_system):
            user_base_dir = os.environ['HOME']
        if user_base_dir is not None and os.path.isdir(user_base_dir):
            return user_base_dir
        return None

    def dark_mode(self, dark_mode: bool = None) -> bool:
        if dark_mode is not None:
            self._config['COLOURS']['dark_mode'] = str(dark_mode)
        return self._config['COLOURS'].getboolean('dark_mode')

    def semester(self, semester: str = None) -> valid_semester | None:
        if semester is not None and (
                semester.lower() == 'fall' or semester.lower() == 'winter' or semester.lower() == 'summer'):
            self._config['MOST_RECENT']['semester'] = semester.lower()

        # TODO: still not sure if I am doing literals correctly
        summer: Literal['summer'] = 'summer'
        winter: Literal['winter'] = 'winter'
        fall: Literal['fall'] = 'fall'
        valid: dict[str, valid_semester] = {'summer': summer, 'winter': winter, 'fall': fall}

        result: valid_semester = valid.get(self._config['MOST_RECENT'].get('semester', None), None)
        return result

    def current_file(self, file: str | None = None) -> str | None:
        directory = None
        filename = None

        if file is not None and os.path.isfile(file):
            directory = os.path.dirname(os.path.realpath(file))
            filename = os.path.basename(file)
            if self.semester() == 'fall':
                self._config['MOST_RECENT']['fall_directory'] = directory
                self._config['MOST_RECENT']['fall_last_file'] = filename
            elif self.semester() == 'winter':
                self._config['MOST_RECENT']['winter_directory'] = directory
                self._config['MOST_RECENT']['winter_last_file'] = filename
            elif self.semester() == 'summer':
                self._config['MOST_RECENT']['summer_directory'] = directory
                self._config['MOST_RECENT']['summer_last_file'] = filename
            else:
                self._config['MOST_RECENT']['fall_directory'] = directory
                self._config['MOST_RECENT']['fall_last_file'] = filename

        else:
            if self.semester() == 'fall':
                directory = self._config['MOST_RECENT'].get('fall_directory', None)
                filename = self._config['MOST_RECENT'].get('fall_last_file', None)
            elif self.semester() == 'winter':
                directory = self._config['MOST_RECENT'].get('winter_directory', None)
                filename = self._config['MOST_RECENT'].get('winter_last_file', None)
            elif self.semester() == 'winter':
                directory = self._config['MOST_RECENT'].get('summer_directory', None)
                filename = self._config['MOST_RECENT'].get('summer_last_file', None)
            else:
                directory = self._config['MOST_RECENT'].get('fall_directory', None)
                filename = self._config['MOST_RECENT'].get('fall_last_file', None)

        if directory is not None and filename is not None:
            if os.path.isfile(directory + "/" + filename):
                y = os.path.realpath(directory + "/" + filename)
                return os.path.realpath(directory + "/" + filename)
        return None

    def current_dir(self, new_dir: str | None = None) -> str | None:
        directory = None

        if new_dir is not None and os.path.isdir(new_dir):
            directory = os.path.dirname(os.path.dirname(os.path.realpath(new_dir)))
            if self.semester() == 'fall':
                self._config['MOST_RECENT']['fall_directory'] = directory
            elif self.semester() == 'winter':
                self._config['MOST_RECENT']['winter_directory'] = directory
            elif self.semester() == 'summer':
                self._config['MOST_RECENT']['summer_directory'] = directory

        else:
            if self.semester() == 'fall':
                directory = self._config['MOST_RECENT'].get('fall_directory', None)
            if self.semester() == 'winter':
                directory = self._config['MOST_RECENT'].get('winter_directory', None)
            if self.semester() == 'winter':
                directory = self._config['MOST_RECENT'].get('summer_directory', None)

        if directory is not None:
            if os.path.isdir(directory):
                return os.path.realpath(directory)
        return None


def _read_ini() -> cp.ConfigParser:
    """if the ini file can be found, read it, if the config file cannot be found, use defaults"""
    ini_file = _get_app_data_location("preferences.csv")
    config = cp.ConfigParser()

    # ini file exists, read it
    if ini_file and os.path.exists(ini_file):
        config.read(ini_file)
        return config

    # if ini file doesn't exist, create default info
    config['MOST_RECENT'] = {}

    config['MOST_RECENT']['fall_directory'] = ''
    config['MOST_RECENT']['fall_last_file'] = ''
    config['MOST_RECENT']['winter_directory'] = ''
    config['MOST_RECENT']['winter_file'] = ''
    config['MOST_RECENT']['summer_directory'] = ''
    config['MOST_RECENT']['summer_last_file'] = ''
    config['MOST_RECENT']['semester'] = 'fall'
    config['COLOURS'] = {}
    config['COLOURS']['dark_mode'] = "yes"
    return config


def _get_app_data_location(ini_file_name: str) -> Optional[str]:
    operating_system = platform.system().lower()
    sub_dir = "scheduling_and_allocation"

    user_base_dir = None
    app_dir = None
    if re.match(r'win', operating_system):
        user_base_dir = os.environ['APPDATA'] if os.environ['AppData'] else os.environ['USERPROFILE']
        app_dir = user_base_dir + "/" + sub_dir
    elif re.search('darwin', operating_system):
        user_base_dir = os.environ['HOME']
        app_dir = user_base_dir + "/." + sub_dir

    if not (app_dir and os.path.exists(app_dir)):
        try:
            os.mkdir(app_dir)
        except Exception:
            return None

    ini_file = user_base_dir + sub_dir + "/" + ini_file_name
    return ini_file


def _write_ini(config: cp.ConfigParser):
    """write preferences in a safe place (it's secret, ha! ha!)"""
    ini_file = _get_app_data_location("preferences.csv")
    if ini_file is None:
        return

    with open(ini_file, 'w') as configfile:
        config.write(configfile)
