import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

from PerlLib import Colours
from Tk import InitGui
from tkinter import Tk as root
from tkinter.font import Font

class FontsAndColoursTk:
    colours : dict[str, str]
    fonts : dict[str, Font]

    def __init__(self, mw : root):
        FontsAndColoursTk.setup(mw)

    @staticmethod
    def setup(mw : root):
        # Gets and sets the colours and fonts
        FontsAndColoursTk.colours, FontsAndColoursTk.fonts = InitGui.set(mw)

        # Hard code the colours
        FontsAndColoursTk.colours = {
            'WorkspaceColour'           : "#eeeeee",
            "WindowForeground"          :  "black",
            "SelectedBackground"        :  "#cdefff",
            "SelectedForeground"        :  "#0000ff",
            "DarkBackground"            :  "#cccccc",
            "ButtonBackground"          :  "#abcdef",
            "ButtonForeground"          :  "black",
            "ActiveBackground"          :  "#89abcd",
            "highlightbackground"       :  "#0000ff",
            "ButtonHighlightBackground" :  "#ff0000",
            "DataBackground"            :  "white",
            "DataForeground"            :  "black",
        }
        Colours.SetSystemColours(mw, FontsAndColoursTk.colours)
        mw.configure(background = FontsAndColoursTk.colours['WorkspaceColour'])