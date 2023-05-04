# COMPLETED
from . import Colour
import platform
import re
import os
from tkinter import Tk

O = platform.system().lower()

# =================================================================
# GetSystemColours
# =================================================================
def GetSystemColours(theme : str = '') -> dict[str, str]:
    """Gets the system colours from the user default settings
    
    Returns colour hash"""
    
    invert = False
    if theme == '-invert' or theme == 'invert':
        invert = True
        theme = ''
    
    colours = dict()

    # --------------------------------------------------------------
	# mac default colour palette
	# --------------------------------------------------------------
    colours['WindowHighlight']  = "#f1efec"
    colours['WorkspaceColour']  = "#e3e3dd"
    colours['ButtonBackground'] = "#e3e3dd"
    colours['DataBackground']   = "#ffffff"
    colours["unknown1"]         = "#68cea600a0e6"
    colours["unknown2"]         = "#8d40ad03c700"

    # --------------------------------------------------------------
	# if solaris or unix, read the gnome theme / dt.resource file
	# --------------------------------------------------------------
    if re.match(r'(solaris|unix|darwin)', O)\
        and os.path.isfile('/usr/share/themes/Simple/gtk-2.0/gtkrc'):
        _read_gtk_palette(theme, colours)
    
    elif re.match(r'(solaris|unix|darwin)', O):
        _read_dt_palette(colours)
    
    # --------------------------------------------------------------
	# if windows, try this
	# --------------------------------------------------------------
    if re.match('windows', O):
        _read_windows_palette(theme, colours)
    
	# --------------------------------------------------------------
	# Invert Colours
	# --------------------------------------------------------------
    if (invert):
        for col in colours:
            hsl = Colour.hsl(colours[col])
            hsl[2] = abs(0.9 * hsl[2] - 1)
            colours[col] = Colour.hsl_from_percent(*hsl)

	# --------------------------------------------------------------
	# adjust for possible missing colours
	# --------------------------------------------------------------

    # should never happen, but better to be safe
    if 'WorkspaceColour' not in colours: colours['WorkspaceColour'] = '#FFFFFF'

    # data foreground
    if 'DataForeground' not in colours:
        if 'DataBackground' in colours and Colour.is_light(colours['DataBackground']):
            colours['DataForeground'] = "#000000"
        else: colours['DataForeground'] = '#FFFFFF'
    
    # a darker background/lighter colour for unused tabs
    if 'DataBackground' in colours and Colour.is_light(colours['DataBackground']):
        colours['DarkBackground'] = Colour.darken(colours['WorkspaceColour'], 10)
    else: colours['DarkBackground'] = Colour.darken(colours['WorkspaceColour'], -10)

    if 'ButtonBackground' not in colours:
        colours['ButtonBackground'] = colours['WorkspaceColour']
    
    # a darker/lighter background colour for selections in lists
    if 'DataBackground' in colours and Colour.is_light(colours['DataBackground']):
        colours['SelectedBackground'] = Colour.darken(colours['DataBackground'], 10)
        colours['SelectedForeground'] = '#000000'
    else:
        colours['SelectedBackground'] = Colour.darken(colours['DataBackground'], -10)
        colours['SelectedForeground'] = '#FFFFFF'
    
    # default foregrounds (white or black depending if colour is dark or not)
    if 'WindowForeground' not in colours:
        if Colour.is_light(colours['WorkspaceColour']):
            colours['WindowForeground'] = '#000000'
        else: colours['WindowForeground'] = '#FFFFFF'
    
    if 'ButtonForeground' not in colours:
        if Colour.is_light(colours['ButtonBackground']):
            colours['ButtonForeground'] = '#000000'
        else: colours['ButtonForeground'] = '#FFFFFF'
    
    if Colour.is_light(colours['ButtonBackground']):
        colours['ActiveBackground'] = Colour.darken(colours['ButtonBackground'], 10)
    else: colours['ActiveBackground'] = Colour.lighten(colours['ButtonBackground'], 10)

    return colours

# =================================================================
# SetSystemColours
# =================================================================
def SetSystemColours(mw : Tk, colours : dict[str, str]):
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
        if k not in colours: colours[k] = None
    
    mw.option_get


    # option_add might not exist, deal with it if not
    
    # generic
    _option_add(mw, "*background", colours['WorkspaceColour'])
    _option_add(mw, '*background',                      colours['WorkspaceColour'])
    _option_add(mw, '*foreground',                      colours['WindowForeground'])
    _option_add(mw, '*selectBackground',                colours['SelectedBackground'])
    _option_add(mw, '*selectForeground',                colours['SelectedForeground'])
    _option_add(mw, '*Scrollbar.troughColor',           colours['DarkBackground'])

    # buttons
    _option_add(mw, "*Button.background",               colours['ButtonBackground'])
    _option_add(mw, "*Button.foreground",               colours['ButtonForeground'])
    _option_add(mw, "*Button.activeBackground",         colours['ActiveBackground'])
    _option_add(mw, "*Button.activeForeground",         colours['ButtonForeground'])
    _option_add(mw, "*Button.highlightBackground",      colours['ButtonHighlightBackground'])

    # radio buttons
    _option_add(mw, "*Radiobutton.activeBackground",    colours['DarkBackground'])
    _option_add(mw, "*Radiobutton.foreground",          colours['WindowForeground'])
    _option_add(mw, "*Radiobutton.background",          colours['WorkspaceColour'])
    _option_add(mw, "*Radiobutton.highlightBackground", colours['WorkspaceColour'])
    _option_add(mw, "*Radiobutton.activeForeground",    colours['WindowForeground'])
    if re.match('windows', O):
        _option_add(mw, "*Radiobutton.selectColor",     colours['DataBackground'])
    
    # check buttons
    _option_add(mw, '*Checkbutton.activeBackground',    colours['DarkBackground'])
    _option_add(mw, '*Checkbutton.foreground',          colours['WindowForeground'])
    _option_add(mw, '*Checkbutton.background',          colours['WorkspaceColour'])
    _option_add(mw, '*Checkbutton.activeForeground',    colours['WindowForeground'])
    _option_add(mw, '*Checkbutton.highlightBackground', colours['WorkspaceColour'])
    if re.match('windows', O):
        _option_add(mw, '*Checkbutton.selectColor',     colours['DataBackground'])
    
    # lists and entries
    _option_add(mw, '*Entry.foreground',                colours['DataForeground'])
    _option_add(mw, '*Entry.background',                colours['DataBackground'])
    _option_add(mw, '*Listbox.foreground',              colours['DataForeground'])
    _option_add(mw, '*Listbox.background',              colours['DataBackground'])
    _option_add(mw, '*BrowseEntry.foreground',          colours['DataForeground'])
    _option_add(mw, '*BrowseEntry.background',          colours['DataBackground'])

    # menu
    _option_add(mw, '*Menu.activeBackground',           colours['DarkBackground'])
    _option_add(mw, '*Menu.activeForeground',           colours['WindowForeground'])

    # trees
    _option_add(mw, '*DynamicTree.foreground',          colours['DataForeground'])
    _option_add(mw, '*DynamicTree.background',          colours['DataBackground'])
    _option_add(mw, '*EasyDir.foreground',              colours['DataForeground'])
    _option_add(mw, '*EasyDir.background',              colours['DataBackground'])

    # text boxes
    _option_add(mw, '*Text.foreground',                 colours['DataForeground'])
    _option_add(mw, '*Text.background',                 colours['DataBackground'])
    _option_add(mw, '*ROText.foreground',               colours['DataForeground'])
    _option_add(mw, '*ROText.background',               colours['DataBackground'])

    # notebook
    _option_add(mw, "*NoteBook.inactiveBackground",     colours['DarkBackground'])
    _option_add(mw, "*NoteBook.background",             colours['WorkspaceColour'])
    _option_add(mw, "*NoteBook.backpagecolour",         colours['WorkspaceColour'])

def _option_add(mw : Tk, option : str, new_value):
    """Sets the provided option on mw. If new_value is none, does nothing"""
    if new_value: mw.option_add(option, new_value)

# =================================================================
# _read_dt_palette
# =================================================================
def _read_dt_palette(colours : dict[str, str]):
    # define resource file
    home = os.environ("HOME")
    file = "/.dt/sessions/current/dt.resources"

    # if resource file exists, read it to find name of user palette
    if os.path.isfile(file):
        f = open(f"{home}/{file}", 'r')
        for l in f.readlines():
            if match := re.match(r'OpenWindows\.(\w+)\:\s+(\#[0-9A-F]*)\s*$', l):
                colours[match.group(1)] = match.group(2)
            if match := re.search(r'ColorPalette:\s+(.*)'):
                palette = match.group(1)
        f.close()
        # what is the point of this?
        if 'WorkspaceColour' in colours and colours['WorkspaceColour']:
            colours['WorkspaceColour'] = colours['WorkspaceColour']
    
    if palette:
        palette_file = '/usr/dt/share/palettes/' + palette
        if os.path.isfile(f'{home}/.dt/palettes/{palette}'):
            palette_file = f'{home}/.dt/palettes/{palette}'
        
        f = open(palette_file, 'r')
        colours['WindowHighlight']  = f.readline().rstrip("\n")
        colours['WorkspaceColour']  = f.readline().rstrip("\n")
        colours['ButtonBackground'] = f.readline().rstrip("\n")
        colours['DataBackground']   = f.readline().rstrip("\n")
        colours['unknown1']         = f.readline().rstrip("\n")
        colours['unknown2']         = f.readline().rstrip("\n")

        f.close()

# =================================================================
# _read_gtk_palette
# =================================================================
def _read_gtk_palette(palette : str, colours : dict[str, str]):
    # get the user defined config file for gnome
    home = os.environ("HOME")
    file = r"/.gconf/desktop/gnome/interface/%gconf.xml"

    # read config file to determine which theme unless palette already defined
    if not palette and os.path.isfile(file):
        f = open(f"{home}/{file}", 'r')
        for l in f.readlines():
            if match := re.match(r'OpenWindows\.(\w+)\:\s+(\#[0-9A-F]*)\s*$', l):
                colours[match.group(1)] = match.group(2)
            if match := re.search(r'ColorPalette:\s+(.*)'):
                palette = match.group(1)
        f.close()
        # what is the point of this?
        if 'WorkspaceColour' in colours and colours['WorkspaceColour']:
            colours['WorkspaceColour'] = colours['WorkspaceColour']
    
    # open and read palette file
    if palette:
        palette_file = '/usr/dt/share/palettes/' + palette
        if os.path.isfile(f'{home}/.dt/palettes/{palette}'):
            palette_file = f'{home}/.dt/palettes/{palette}'
        
        f = open(palette_file, 'r')
        colours['WindowHighlight']  = f.readline().rstrip("\n")
        colours['WorkspaceColour']  = f.readline().rstrip("\n")
        colours['ButtonBackground'] = f.readline().rstrip("\n")
        colours['DataBackground']   = f.readline().rstrip("\n")
        colours['unknown1']         = f.readline().rstrip("\n")
        colours['unknown2']         = f.readline().rstrip("\n")

        f.close()

# =================================================================
# _read_gtk_palette
# =================================================================
def _read_gtk_palette(palette : str, colours : dict[str, str]):
    # get the user defined config file for gnome
    home = os.environ("HOME")
    file = r"/.gconf/desktop/gnome/interface/%gconf.xml"

    # read config file to determine which theme unless palette already defined
    if not palette and os.path.isfile(file):
        f = open(f"{home}/{file}", 'r')
        theme = False
        for l in f.readlines():
            if re.search(r'entry name="gtk_theme"'): theme = True
            if theme and (match := re.search(r'<stringvalue>(.*)</stringvalue>')):
                palette = match.group(1)
                break
        f.close()
    
    # read the themed file (use Simple as starting point, then modify accoding to theme)
    for theme in ['Simple', palette]:
        palette_file = f'/usr/share/themes/{theme}/gtk-2.0/gtkrc'
        if os.path.isfile(palette_file):
            f = open(palette_file, 'r')
            for l in f.readlines():
                match = re.search(r'/style\s*"(.*)"', l)
                if match.group(1) == 'default':
                    if (r := re.search(r'/fg\[ACTIVE\]\s*=\s*"(.*)"')):
                        colours['WindowHighlight'] = r.group(1)
                    if (r := re.search(r'/fg\[NORMAL\]\s*=\s*"(.*)"')):
                        colours['WindowForeground'] = r.group(1)
                    if (r := re.search(r'/base\[NORMAL\]\s*=\s*"(.*)"')):
                        colours['DataBackground'] = r.group(1)
                    if (r := re.search(r'/text\[NORMAL\]\s*=\s*"(.*)"')):
                        colours['DataForeground'] = r.group(1)
                    if (r := re.search(r'/bg\[NORMAL\]\s*=\s*"(.*)"')):
                        colours['WorkspaceColour'] = r.group(1)
                    if (r := re.search(r'/base\[SELECTED\]\s*=\s*"(.*)"')):
                        colours['ButtonBackground'] = r.group(1)
            f.close()


# =================================================================
# _read_windows_palette
# =================================================================
def _read_windows_palette(scheme : str, colours : dict[str, str]):
    # scheme is currently unused
    
    # open registry
    try: import winreg
    except: return

    # get the current colour scheme
    x = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Colors")

    # get the colour from the registry
        # uses QueryValueEx - QueryValue failed to find the key for some reason
    colours['WindowHighlight'] = _key_to_colour(winreg.QueryValueEx(x, 'HilightText')[0])
    colours['WindowForeground'] = _key_to_colour(winreg.QueryValueEx(x, 'MenuText')[0])
    colours['DataBackground'] = _key_to_colour(winreg.QueryValueEx(x, 'Window')[0])
    colours['DataForeground'] = _key_to_colour(winreg.QueryValueEx(x, 'WindowText')[0])
    colours['WorkspaceColour'] = _key_to_colour(winreg.QueryValueEx(x, 'ActiveBorder')[0])
    colours['ButtonBackground'] = _key_to_colour(winreg.QueryValueEx(x, 'ButtonFace')[0])

def _key_to_colour(key : str):
    return Colour.rgb_from_percent(*map(lambda a: int(a)/255, key.split(" ")))
