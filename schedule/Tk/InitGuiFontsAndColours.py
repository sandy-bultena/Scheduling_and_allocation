"""Sets up the standard Tk properties (fonts, colours)"""

from __future__ import annotations
from tkinter import Tk
from tkinter.font import Font
import platform
import re
from typing import Literal

import schedule.UsefulClasses.Colour as colour

operating_system = platform.system().lower()

# old (or maybe new default colours?)
# _old_default_colours =
# {  'WorkspaceColour': "#eeeeee",
#     "WindowForeground": "black",
#     "SelectedBackground": "#cdefff",
#     "SelectedForeground": "#0000ff",
#     "DarkBackground": "#cccccc",
#     "ButtonBackground": "#abcdef",
#     "ButtonForeground": "black",
#     "ActiveBackground": "#89abcd",
#     "highlightbackground": "#0000ff",
#     "ButtonHighlightBackground": "#ff0000",
#     "DataBackground": "white",
#     "DataForeground": "black",
#    }

available_colours = Literal[
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
    'DisabledBackground',
    'DisabledForeground',
]

available_fonts = Literal[
                  'normal',
                  'bold',
                  'big',
                  'bigbold',
                  'fixed',
                  'small':
                  ]

colours: dict[available_colours, str] = dict()
fonts: dict[available_fonts, Font] = dict()


def set_default_fonts_and_colours(mw: Tk, font_size: int = 12, dark_mode: bool = False):
    global colours
    global fonts
    colours = _get_system_colours(dark=dark_mode)
    _set_system_colours(mw, colours)
    mw.configure(background=colours['WorkspaceColour'])

    fonts = _define_fonts(mw, font_size)
    mw.option_add("*Font", fonts['normal'],)
    return colours, fonts


def _define_fonts(mw: Tk, my_size: int = 12) -> dict[available_fonts, Font]:
    # define normal font
    size = my_size
    if re.search('win', operating_system):
        size -= 2
    family = 'arial'
    if re.search('darwin', operating_system):
        family = 'lucidia'
        size += 3

    set_props = {
        'slant': 'roman', 'underline': 0, 'overstrike': 0
    }

    normal_weight: Literal['normal'] = 'normal'
    bold_weight: Literal['bold'] = 'bold'
    normal_size = size
    bigger_size = size + 2
    normal_font = family
    fixed_font = 'courier new'

    # make fonts
    fonts: [available_fonts, str] = {
        'normal': Font(mw, **set_props, weight=normal_weight, size=normal_size, family=normal_font),
        'bold': Font(mw, **set_props, weight=bold_weight, size=normal_size, family=normal_font),
        'big': Font(mw, **set_props, weight=normal_weight, size=bigger_size, family=normal_font),
        'bigbold': Font(mw, **set_props, weight=bold_weight, size=bigger_size, family=normal_font),
        'fixed': Font(mw, **set_props, weight=bold_weight, size=size + 1, family=fixed_font),
        'small': Font(mw, **set_props, weight=normal_weight, size=size - 2, family=normal_font)
    }

    return fonts


# =================================================================
# _get_system_colours
# =================================================================
def _get_system_colours(dark: bool = False) -> dict[available_colours, str]:
    """
    Defines the colours for the Tk app.
    Does not get the system colours anymore.
    Times have changed."""

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

    # a darker/lighter background colour for unused tabs
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

    # a darker/lighter background colour for disabled widgets
    if 'DataBackground' in colours and colour.is_light(colours['DataBackground']):
        colours['DisabledBackground'] = colour.darken(colours['DataBackground'], 20)
        colours['DisabledForeground'] = '#000000'
    else:
        colours['DisabledBackground'] = colour.darken(colours['DataBackground'], -20)
        colours['DisabledForeground'] = '#FFFFFF'

    # mac won't change button colours
    if re.match('darwin', operating_system):
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
# _set_system_colours
# =================================================================
def _set_system_colours(mw: Tk, colours: dict[str, str | None]):
    """Using colour array and main window, set_default_fonts_and_colours up some standard defaults for Tk widgets"""

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
        'DisabledBackground',
        'DisabledForeground',

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
    if re.match('windows', operating_system):
        _option_add(mw, "*Radiobutton.selectColor", colours['DataBackground'])

    # check buttons
    _option_add(mw, '*Checkbutton.activeBackground', colours['DarkBackground'])
    _option_add(mw, '*Checkbutton.foreground', colours['WindowForeground'])
    _option_add(mw, '*Checkbutton.background', colours['WorkspaceColour'])
    _option_add(mw, '*Checkbutton.activeForeground', colours['WindowForeground'])
    _option_add(mw, '*Checkbutton.highlightBackground', colours['WorkspaceColour'])
    if re.match('windows', operating_system):
        _option_add(mw, '*Checkbutton.selectColor', colours['DataBackground'])

    # lists and entries
    _option_add(mw, '*Entry.foreground', colours['DataForeground'])
    _option_add(mw, '*Entry.background', colours['DataBackground'])
    _option_add(mw, '*Entry.disabledforeground', colours['DisabledForeground'])
    _option_add(mw, '*Entry.disabledbackground', colours['DisabledBackground'])
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

    # _notebook
    _option_add(mw, "*NoteBook.inactiveBackground", colours['DarkBackground'])
    _option_add(mw, "*NoteBook.background", colours['WorkspaceColour'])
    _option_add(mw, "*NoteBook.backpagecolour", colours['WorkspaceColour'])


def _option_add(mw: Tk, option: str, new_value):
    """Sets the provided option on _mw. If new_value is none, does nothing"""
    if new_value:
        mw.option_add(option, new_value)
