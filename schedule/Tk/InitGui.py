"""Sets up the standard Tk properties (fonts, colours)"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

from PerlLib import Colours
from tkinter import Tk
from tkinter.font import Font
import platform, re

O = platform.system().lower()

def set(mw : Tk, my_size : int = 12):
    # colours
    colours : dict[str, str] = Colours.GetSystemColours()
    Colours.SetSystemColours(mw, colours)
    mw.configure(background = colours['WorkspaceColour'])

    # define normal font
    size = my_size
    if re.search('win', O): size -= 2
    # currently unused var
    family = 'arial'
    if re.search('darwin', O):
        family = 'lucida'
        size += 2

    set_props = {
        'slant': 'roman', 'underline': 0, 'overstrike': 0
    }

    nor_w = 'normal'
    bol_w = 'bold'
    nor_s = size
    bol_s = size + 2
    nor_f = 'arial'
    fix_f = 'courier new'

    # make fonts
    fonts = {
        'normal' : Font(mw, **set_props, weight = nor_w, size = nor_s, family = nor_f),
        'bold'   : Font(mw, **set_props, weight = bol_w, size = nor_s, family = nor_f),
        'big'    : Font(mw, **set_props, weight = nor_w, size = bol_s, family = nor_f),
        'bigbold': Font(mw, **set_props, weight = bol_w, size = bol_s, family = nor_f),
        'fixed'  : Font(mw, **set_props, weight = bol_w, size = size + 1, family = fix_f),
        'small'  : Font(mw, **set_props, weight = nor_w, size = size - 2, family = nor_f)
    }

    mw.option_add(fonts['normal'], "*font")

    return colours, fonts