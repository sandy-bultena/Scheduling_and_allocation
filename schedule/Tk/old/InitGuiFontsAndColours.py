"""Sets up the standard Tk properties (fonts, colors)"""

from __future__ import annotations
from tkinter import Tk, TclError
from tkinter.font import Font
import platform
import re
from typing import Literal, Optional

import schedule.Utilities.Colour as Colour

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
            for col in vars(self):

                # Note: button colors don't work on MAC, so skip
                if re.search("button", col.lower()):
                    if re.match('darwin', operating_system):
                        continue

                h, s, l = Colour.hsl(getattr(self, col))
                l = abs(0.9 * l - 1)
                setattr(self, col, Colour.get_colour_string_from_hsl(h, s, l))


class TkFonts:
    def __init__(self, mw: Tk, my_size: int = 12):
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
        self.normal: Font = Font(mw, **set_props, weight=normal_weight, size=normal_size, family=normal_font)
        self.bold: Font = Font(mw, **set_props, weight=bold_weight, size=normal_size, family=normal_font)
        self.big: Font = Font(mw, **set_props, weight=normal_weight, size=bigger_size, family=normal_font)
        self.bigbold: Font = Font(mw, **set_props, weight=bold_weight, size=bigger_size, family=normal_font)
        self.fixed: Font = Font(mw, **set_props, weight=bold_weight, size=size + 1, family=fixed_font)
        self.small: Font = Font(mw, **set_props, weight=normal_weight, size=size - 2, family=normal_font)


colours: TkColours = TkColours()
fonts: Optional[TkFonts] = None


def set_default_fonts_and_colours(mw: Tk, font_size: int = 12, dark_mode: bool = False):
    global fonts
    global colours
    colours = TkColours(mw, dark=dark_mode)
    set_system_colours(mw, colours)
    mw.configure(background=colours.WorkspaceColour)

    fonts = TkFonts(mw, font_size)
    mw.option_add("*Font", fonts.normal, )
    return colours, fonts


# =================================================================
# set_system_colours
# =================================================================
def set_system_colours(mw: Tk, colors: TkColours):
    """Using Colour array and main window, set_default_fonts_and_colours up
    some standard defaults for Tk widgets"""

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
    _option_add(mw, '*Entry.highlightebackground', colors.WorkspaceColour)
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
