"""Sets up the standard Tk properties (fonts, colors)"""

from __future__ import annotations
from tkinter import Tk, TclError
from tkinter.font import Font
import platform
import re
from typing import Literal, Optional

import schedule.UsefulClasses.Colour as Colour

operating_system = platform.system().lower()


class TkColours:
    """Defines colour scheme """

    def __init__(self, tk_root: Optional[Tk] = None, theme='mac', dark=False):
        # Defaults to MAC Colours
        window_background_color: Optional[str] = None
        pressed_button_text_color: Optional[str] = None
        text_color: Optional[str] = None
        text_background_color: Optional[str] = None
        selected_text_background_color: Optional[str] = None
        selected_text_color: Optional[str] = None

        # ============================================================================
        # get system colours (mac) ... not sure about if this works on windows
        # ============================================================================
        if tk_root:
            try:
                (r, g, b) = tk_root.winfo_rgb('systemWindowBackgroundColor')
                window_background_color = Colour.get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemPressedButtonTextColor')
                pressed_button_text_color = Colour.get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemTextColor')
                text_color = Colour.get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemTextBackgroundColor')
                text_background_color = Colour.get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemSelectedTextBackgroundColor')
                selected_text_background_color = Colour.get_colour_string_from_rgb(r / 65536.0, g / 65536.0,
                                                                                   b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemSelectedTextColor')
                selected_text_color = Colour.get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

        # default is mac
        self.SelectedForeground: str = selected_text_color if selected_text_color else "#000000"
        self.SelectedBackground: str = selected_text_background_color if selected_text_background_color \
            else "#eab9ff"
        self.DataBackground = text_background_color if text_background_color else "#ffffff"
        self.WorkspaceColour: str = window_background_color if window_background_color else "#eeeeee"
        self.ButtonPress: str = pressed_button_text_color if pressed_button_text_color else "#ffffff"
        self.DataForeground = text_color if text_color else "#000000"
        self.HighlightColor = self.DataForeground
        self.WindowForeground: str = self.DataForeground
        self.ButtonBackground: str = self.WorkspaceColour
        self.ActiveBackground: str = self.WorkspaceColour
        self.HighlightBackground: str = self.WorkspaceColour
        self.ButtonForeground: str = "#000000"
        self.DarkBackground: str = Colour.darken(self.WorkspaceColour, 20)
        self.DisabledBackground: str = "#a3a3a3"
        self.DirtyColour: str = "#880000"
        self.DisabledBackground = "#a3a3a3"
        self.DisabledForeground = "#000000"

        # ============================================================================
        # if dark mode, just invert all the colours
        # ============================================================================
        if dark:
            print ("Converting to darkmode")
            for col in vars(self):

                # Note: button colors don't work on MAC, so skip
                if re.search("button", col.lower()):
                    if re.match('darwin', operating_system):
                        continue

                print(f"{col} was {getattr(self, col)}")
                h, s, l = Colour.hsl(getattr(self, col))
                print(f"({h},{s},{l}")
                l = abs(0.9 * l - 1)
                print(f"({h},{s},{l}")
                print(f"... setting {col} to {Colour.get_colour_string_from_hsl(h, s, l)}")
                setattr(self, col, Colour.get_colour_string_from_hsl(h, s, l))




available_fonts = Literal[
                  'normal',
                  'bold',
                  'big',
                  'bigbold',
                  'fixed',
                  'small':
                  ]

fonts: dict[available_fonts, Font] = dict()
colours: TkColours = TkColours()

def set_default_fonts_and_colours(mw: Tk, font_size: int = 12, dark_mode: bool = False):
    global fonts
    global colours
    colours = TkColours(mw, dark=dark_mode)
    set_system_colours(mw, colours)
    mw.configure(background=colours.WorkspaceColour)

    fonts = _define_fonts(mw, font_size)
    mw.option_add("*Font", fonts['normal'], )
    return colours, fonts


def _define_fonts(mw: Tk, my_size: int = 12) -> dict[available_fonts, Font]:
    global fonts
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
    fonts = {
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
def _get_system_colours(root: Optional[Tk] = None, dark: bool = False) -> TkColours:
    """
    Defines the colors for the Tk app.
    Does not get the system colors anymore.
    Times have changed."""

    global colours
    colours = TkColours(root)

    # --------------------------------------------------------------
    # Invert Colours
    # --------------------------------------------------------------
    if dark:
        for col in vars(colours):
            # Note: button colors don't work on MAC, so skip
            if not re.match('darwin', operating_system):
                colours.ButtonBackground = colours.WorkspaceColour

            print(f"{col} was {getattr(colours, col)}")
            h, s, l = Colour.hsl(getattr(colours, col))
            print(f"({h},{s},{l}")
            l = abs(0.9 * l - 1)
            print(f"({h},{s},{l}")
            print(f"... setting {col} to {Colour.get_colour_string_from_hsl(h, s, l)}")
            setattr(colours, col, Colour.get_colour_string_from_hsl(h, s, l))

    # --------------------------------------------------------------
    # adjust for consistency
    # --------------------------------------------------------------

    # a darker/lighter background Colour for unused tabs
    if Colour.is_light(colours.DataBackground):
        colours.DarkBackground = Colour.darken(colours.WorkspaceColour, 10)
    else:
        colours.DarkBackground = Colour.darken(colours.WorkspaceColour, -10)

    # a darker/lighter background Colour for selections in lists
    if Colour.is_light(colours.DataBackground):
        colours.SelectedBackground = Colour.darken(colours.DataBackground, 30)
        colours.DisabledBackground = Colour.darken(colours.DataBackground, 20)
        colours.SelectedForeground = '#000000'
        colours.DisabledForeground = '#000000'
    else:
        colours.SelectedBackground = Colour.darken(colours.DataBackground, -30)
        colours.DisabledBackground = Colour.darken(colours.DataBackground, -20)
        colours.SelectedForeground = '#FFFFFF'
        colours.DisabledForeground = '#FFFFFF'

    # default foregrounds (white or black depending on if Colour is dark or not)
    if Colour.is_light(colours.WorkspaceColour):
        colours.WindowForeground = '#000000'
    else:
        colours.WindowForeground = '#FFFFFF'
        colours.DirtyColour = '#ff0000'

    if Colour.is_light(colours.ButtonBackground):
        colours.ButtonForeground = '#000000'
        colours.ActiveBackground = Colour.darken(colours.ButtonBackground, 10)
    else:
        colours.ButtonForeground = '#FFFFFF'
        colours.ActiveBackground = Colour.lighten(colours.ButtonBackground, 10)

    return colours


# =================================================================
# set_system_colours
# =================================================================
def set_system_colours(mw: Tk, colors: TkColours):
    """Using Colour array and main window, set_default_fonts_and_colours up some standard defaults for Tk widgets"""

    """





highlightbackground − Background color of the highlight region when the widget has focus.

highlightcolor − Foreground color of the highlight region when the widget has focus.



"""
    # generic
    #    activebackground − Background color for the widget when the widget is active.
    #    activeforeground − Foreground color for the widget when the widget is active.
    #    background − Background color for the widget. This can also be represented as bg.
    #    disabledforeground − Foreground color for the widget when the widget is disabled.
    #    highlightbackground − Background color of the highlight region when the widget has focus.
    #    highlightcolor − Foreground color of the highlight region when the widget has focus.
    #    foreground − Foreground color for the widget. This can also be represented as fg.
    #    selectbackground − Background color for the selected items of the widget.
    #    selectforeground − Foreground color for the selected items of the widget.
    _option_add(mw, '*activebackground', colors.ActiveBackground)
    _option_add(mw, '*activeforeground', colors.ButtonPress)
    _option_add(mw, "*background", colors.WorkspaceColour)
    _option_add(mw, "*disabledforeground", colors.DisabledForeground)
    _option_add(mw, "*highlightbackground", colors.HighlightBackground)
    _option_add(mw, "*highlightcolor", colors.HighlightColor)
    _option_add(mw, '*foreground', colors.WindowForeground)
    _option_add(mw, '*selectBackground', colors.SelectedBackground)
    _option_add(mw, '*selectForeground', colors.SelectedForeground)
    _option_add(mw, '*troughColor', colors.DarkBackground)

    # buttons
    _option_add(mw, "*Button.background", colors.ButtonBackground)
    _option_add(mw, "*Button.foreground", colors.ButtonForeground)
    _option_add(mw, "*Button.activeBackground", colors.ActiveBackground)
    _option_add(mw, "*Button.activeForeground", colors.ButtonForeground)
    _option_add(mw, "*Button.highlightBackground", colors.HighlightBackground)

    # radio buttons
    _option_add(mw, "*Radiobutton.activeBackground", colors.DarkBackground)
    _option_add(mw, "*Radiobutton.foreground", colors.WindowForeground)
    _option_add(mw, "*Radiobutton.background", colors.WorkspaceColour)
    _option_add(mw, "*Radiobutton.highlightBackground", colors.WorkspaceColour)
    _option_add(mw, "*Radiobutton.activeForeground", colors.WindowForeground)
    if re.match('windows', operating_system):
        _option_add(mw, "*Radiobutton.selectColor", colors.DataBackground)

    # check buttons
    _option_add(mw, '*Checkbutton.activeBackground', colors.DarkBackground)
    _option_add(mw, '*Checkbutton.foreground', colors.WindowForeground)
    _option_add(mw, '*Checkbutton.background', colors.WorkspaceColour)
    _option_add(mw, '*Checkbutton.activeForeground', colors.WindowForeground)
    _option_add(mw, '*Checkbutton.highlightBackground', colors.WorkspaceColour)
    if re.match('windows', operating_system):
        _option_add(mw, '*Checkbutton.selectColor', colors.DataBackground)

    # lists and entries
    _option_add(mw, '*Entry.foreground', colors.DataForeground)
    _option_add(mw, '*Entry.background', colors.DataBackground)
    _option_add(mw, '*Entry.disabledforeground', colors.DisabledForeground)
    _option_add(mw, '*Entry.disabledbackground', colors.DisabledBackground)
    _option_add(mw, '*Listbox.foreground', colors.DataForeground)
    _option_add(mw, '*Listbox.background', colors.DataBackground)
    _option_add(mw, '*BrowseEntry.foreground', colors.DataForeground)
    _option_add(mw, '*BrowseEntry.background', colors.DataBackground)

    # menu
    _option_add(mw, '*Menu.activeBackground', colors.DarkBackground)
    _option_add(mw, '*Menu.activeForeground', colors.WindowForeground)

    # trees
    _option_add(mw, '*DynamicTree.foreground', colors.DataForeground)
    _option_add(mw, '*DynamicTree.background', colors.DataBackground)
    _option_add(mw, '*EasyDir.foreground', colors.DataForeground)
    _option_add(mw, '*EasyDir.background', colors.DataBackground)

    # text boxes
    _option_add(mw, '*Text.foreground', colors.DataForeground)
    _option_add(mw, '*Text.background', colors.DataBackground)
    _option_add(mw, '*ROText.foreground', colors.DataForeground)
    _option_add(mw, '*ROText.background', colors.DataBackground)

    # _notebook
    _option_add(mw, "*NoteBook.inactiveBackground", colors.DarkBackground)
    _option_add(mw, "*NoteBook.background", colors.WorkspaceColour)
    _option_add(mw, "*NoteBook.backpagecolour", colors.WorkspaceColour)

    # other
    _option_add(mw, '*Scrollbar.troughColor', colors.DarkBackground)


def _option_add(mw: Tk, option: str, new_value):
    """Sets the provided option on _mw. If new_value is none, does nothing"""
    if new_value:
        mw.option_add(option, new_value)
