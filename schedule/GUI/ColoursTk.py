
"""Set the colour palette for Tk objects"""
from __future__ import annotations

import schedule.UsefulClasses.Colour as colour
import platform
import re
from tkinter import Tk

OS_name = platform.system().lower()


# =================================================================
# get_system_colours
# =================================================================
def get_system_colours(dark: bool = False) -> dict[str, str]:
    """Gets the system colours from the user default settings

    Returns colour hash"""

    colours = dict()

    # --------------------------------------------------------------
    # default colour palette
    # --------------------------------------------------------------
    colours['WindowHighlight'] = "#f1efec"
    colours['WorkspaceColour'] = "#e3e3dd"
    colours['ButtonBackground'] = "#e3e3dd"
    colours['DataBackground'] = "#ffffff"
    colours["unknown1"] = "#68cea600a0e6"
    colours["unknown2"] = "#8d40ad03c700"

    # --------------------------------------------------------------
    # Invert Colours
    # --------------------------------------------------------------
    if dark:
        for col in colours:
            h, s, l = colour.hsl(colours[col])
            l = abs(0.9 * l - 1)
            colours[col] = colour.get_colour_string_from_hsl(h, s, l)

    # --------------------------------------------------------------
    # adjust for possible missing colours
    # --------------------------------------------------------------

    # should never happen, but better to be safe
    if 'WorkspaceColour' not in colours:
        colours['WorkspaceColour'] = '#FFFFFF'

    # data foreground
    if 'DataForeground' not in colours:
        if 'DataBackground' in colours and colour.is_light(colours['DataBackground']):
            colours['DataForeground'] = "#000000"
        else:
            colours['DataForeground'] = '#FFFFFF'

    # a darker background/lighter colour for unused tabs
    if 'DataBackground' in colours and colour.is_light(colours['DataBackground']):
        colours['DarkBackground'] = colour.darken(colours['WorkspaceColour'], 10)
    else:
        colours['DarkBackground'] = colour.darken(colours['WorkspaceColour'], -10)

    if 'ButtonBackground' not in colours:
        colours['ButtonBackground'] = colours['WorkspaceColour']

    # a darker/lighter background colour for selections in lists
    if 'DataBackground' in colours and colour.is_light(colours['DataBackground']):
        colours['SelectedBackground'] = colour.darken(colours['DataBackground'], 10)
        colours['SelectedForeground'] = '#000000'
    else:
        colours['SelectedBackground'] = colour.darken(colours['DataBackground'], -10)
        colours['SelectedForeground'] = '#FFFFFF'

    # mac won't change button colours
    if re.match('darwin', OS_name):
        colours['ButtonBackground'] = "#FFFFFF"

    # default foregrounds (white or black depending on if colour is dark or not)
    if 'WindowForeground' not in colours:
        if colour.is_light(colours['WorkspaceColour']):
            colours['WindowForeground'] = '#000000'
        else:
            colours['WindowForeground'] = '#FFFFFF'

    if 'ButtonForeground' not in colours:
        if colour.is_light(colours['ButtonBackground']):
            colours['ButtonForeground'] = '#000000'
        else:
            colours['ButtonForeground'] = '#FFFFFF'

    if colour.is_light(colours['ButtonBackground']):
        colours['ActiveBackground'] = colour.darken(colours['ButtonBackground'], 10)
    else:
        colours['ActiveBackground'] = colour.lighten(colours['ButtonBackground'], 10)

    return colours


# =================================================================
# set_system_colours
# =================================================================
def set_system_colours(mw: Tk, colours: dict[str, str | None]):
    """Using colour array and main window, set up some standard defaults for Tk widgets"""

    # make sure that all expected key values are at least None to avoid KeyNotFound crashes
    keys = [
        'WorkspaceColour',
        'WindowForeground',
        'SelectedBackground',
        'SelectedForeground',
        'DarkBackground',
        'ButtonBackground',
        'ButtonForeground',
        'ActiveBackground',
        'ButtonHighlightBackground',
        'DataBackground',
        'DataForeground',
    ]
    for k in keys:
        if k not in colours:
            colours[k] = None

    # generic
    _option_add(mw, "*background", colours['WorkspaceColour'])
    _option_add(mw, '*background', colours['WorkspaceColour'])
    _option_add(mw, '*foreground', colours['WindowForeground'])
    _option_add(mw, '*selectBackground', colours['SelectedBackground'])
    _option_add(mw, '*selectForeground', colours['SelectedForeground'])
    _option_add(mw, '*Scrollbar.troughColor', colours['DarkBackground'])

    # buttons
    _option_add(mw, "*Button.background", colours['ButtonBackground'])
    _option_add(mw, "*Button.foreground", colours['ButtonForeground'])
    _option_add(mw, "*Button.activeBackground", colours['ActiveBackground'])
    _option_add(mw, "*Button.activeForeground", colours['ButtonForeground'])
    _option_add(mw, "*Button.highlightBackground", colours['ButtonHighlightBackground'])

    # radio buttons
    _option_add(mw, "*Radiobutton.activeBackground", colours['DarkBackground'])
    _option_add(mw, "*Radiobutton.foreground", colours['WindowForeground'])
    _option_add(mw, "*Radiobutton.background", colours['WorkspaceColour'])
    _option_add(mw, "*Radiobutton.highlightBackground", colours['WorkspaceColour'])
    _option_add(mw, "*Radiobutton.activeForeground", colours['WindowForeground'])
    if re.match('windows', OS_name):
        _option_add(mw, "*Radiobutton.selectColor", colours['DataBackground'])

    # check buttons
    _option_add(mw, '*Checkbutton.activeBackground', colours['DarkBackground'])
    _option_add(mw, '*Checkbutton.foreground', colours['WindowForeground'])
    _option_add(mw, '*Checkbutton.background', colours['WorkspaceColour'])
    _option_add(mw, '*Checkbutton.activeForeground', colours['WindowForeground'])
    _option_add(mw, '*Checkbutton.highlightBackground', colours['WorkspaceColour'])
    if re.match('windows', OS_name):
        _option_add(mw, '*Checkbutton.selectColor', colours['DataBackground'])

    # lists and entries
    _option_add(mw, '*Entry.foreground', colours['DataForeground'])
    _option_add(mw, '*Entry.background', colours['DataBackground'])
    _option_add(mw, '*Listbox.foreground', colours['DataForeground'])
    _option_add(mw, '*Listbox.background', colours['DataBackground'])
    _option_add(mw, '*BrowseEntry.foreground', colours['DataForeground'])
    _option_add(mw, '*BrowseEntry.background', colours['DataBackground'])

    # menu
    _option_add(mw, '*Menu.activeBackground', colours['DarkBackground'])
    _option_add(mw, '*Menu.activeForeground', colours['WindowForeground'])

    # trees
    _option_add(mw, '*DynamicTree.foreground', colours['DataForeground'])
    _option_add(mw, '*DynamicTree.background', colours['DataBackground'])
    _option_add(mw, '*EasyDir.foreground', colours['DataForeground'])
    _option_add(mw, '*EasyDir.background', colours['DataBackground'])

    # text boxes
    _option_add(mw, '*Text.foreground', colours['DataForeground'])
    _option_add(mw, '*Text.background', colours['DataBackground'])
    _option_add(mw, '*ROText.foreground', colours['DataForeground'])
    _option_add(mw, '*ROText.background', colours['DataBackground'])

    # notebook
    _option_add(mw, "*NoteBook.inactiveBackground", colours['DarkBackground'])
    _option_add(mw, "*NoteBook.background", colours['WorkspaceColour'])
    _option_add(mw, "*NoteBook.backpagecolour", colours['WorkspaceColour'])


def _option_add(mw: Tk, option: str, new_value):
    """Sets the provided option on mw. If new_value is none, does nothing"""
    if new_value:
        mw.option_add(option, new_value)

