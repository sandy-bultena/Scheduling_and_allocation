from ..PerlLib import Colours
from ..Tk import InitGui
from tkinter import Tk as root
from tkinter.font import Font

# Hard code the colours
colours: dict[str, str] = {
    'WorkspaceColour': "#eeeeee",
    "WindowForeground": "black",
    "SelectedBackground": "#cdefff",
    "SelectedForeground": "#0000ff",
    "DarkBackground": "#cccccc",
    "ButtonBackground": "#abcdef",
    "ButtonForeground": "black",
    "ActiveBackground": "#89abcd",
    "highlightbackground": "#0000ff",
    "ButtonHighlightBackground": "#ff0000",
    "DataBackground": "white",
    "DataForeground": "black",
}

fonts: dict[str, Font]

def setup(mw: root):
    """Gets and sets the colours and fonts"""
    global colours, fonts
    colours, fonts = InitGui.set(mw)

    Colours.set_system_colours(mw, colours)
    mw.configure(background=colours['WorkspaceColour'])


