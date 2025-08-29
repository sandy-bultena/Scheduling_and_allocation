"""Sets up the standard Tk properties (fonts, colors)"""

from __future__ import annotations

import os
from tkinter import Tk, TclError, ttk
from tkinter.font import Font
import platform
import re
from typing import Literal, Optional

import tkinter.font as tkFont

from PIL import Image, ImageDraw, ImageTk

from ..Utilities.Colour import get_colour_string_from_rgb, darken, is_light, lighten, add, \
    hsl, get_colour_string_from_hsl

operating_system = platform.system().lower()

DEFAULT_FONT_SIZE = 10
if "darwin" in operating_system:
    DEFAULT_FONT_SIZE = 13

global img_open, img_close, img_empty


class TkColours:
    """Defines colour scheme """

    def __init__(self, tk_root: Optional[Tk] = None, invert=False, theme='mac'):
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
                window_background_color = get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemPressedButtonTextColor')
                pressed_button_text_color = get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemTextColor')
                text_color = get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemTextBackgroundColor')
                text_background_color = get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemSelectedTextBackgroundColor')
                selected_text_background_color = get_colour_string_from_rgb(r / 65536.0, g / 65536.0,
                                                                                   b / 65536.0)
            except TclError:
                pass

            try:
                (r, g, b) = tk_root.winfo_rgb('systemSelectedTextColor')
                selected_text_color = get_colour_string_from_rgb(r / 65536.0, g / 65536.0, b / 65536.0)
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
        self.DarkBackground: str = darken(self.WorkspaceColour, 20)
        self.DisabledBackground: str = "#a3a3a3"
        self.DirtyColour: str = "#ff8888"
        self.DisabledBackground = "#a3a3a3"
        self.DisabledForeground = "#000000"
        self.DragNDropForeground = self.WindowForeground

        if is_light(self.WorkspaceColour):
            self.DragNDropBackground = darken(self.WorkspaceColour, 25)
            self.DragNDropAllowedBackground = darken(self.WorkspaceColour, 5)
        else:
            self.DragNDropBackground = lighten(self.WorkspaceColour, 25)
            self.DragNDropAllowedBackground = lighten(self.WorkspaceColour, 5)

        self.ButtonHighlight = self.ButtonBackground
        if is_light(self.ButtonHighlight):
            self.ButtonHoverHighlight = darken(self.WorkspaceColour, 25)
            self.ButtonForeground = "#000000"
        else:
            self.ButtonHoverHighlight = lighten(self.WorkspaceColour, 25)
            self.ButtonForeground = "#FFFFFF"

        if is_light(self.WorkspaceColour):
            self.DirtyColour = add("red","#444444")
        else:
            self.DirtyColour = add("red","white")
        # ============================================================================
        # if invert mode, just invert all the colours
        # ============================================================================
        if invert:
            for col in vars(self):

                # Note: button colors don't work on MAC, so skip
                if re.search("button", col.lower()):
                    if re.match('darwin', operating_system):
                        continue

                h, s, l = hsl(getattr(self, col))
                l = abs(0.9 * l - 1)
                setattr(self, col, get_colour_string_from_hsl(h, s, l))

        if os.name == 'darwin' or os.name == "posix":
            # MAC does not allow you to change the background colour of buttons
            self.ButtonForeground = "#000000"

    def __str__(self):
        str: str = ""
        for col in vars(self):
            str += f"{col}: {getattr(self, col)}\n"
        return str


class TkFonts:
    def __init__(self, mw: Tk, my_size: int = DEFAULT_FONT_SIZE):
        default_font = tkFont.nametofont("TkTextFont")
        family = default_font["family"]

        normal_weight: Literal['normal'] = 'normal'
        bold_weight: Literal['bold'] = 'bold'
        normal_size = my_size
        bigger_size = my_size + 2
        normal_font = family
        fixed_font = 'courier new'

        # make fonts
        self.normal: Font = Font(mw, weight=normal_weight, size=normal_size, family=normal_font)
        self.bold: Font = Font(mw, weight=bold_weight, size=normal_size, family=normal_font)
        self.big: Font = Font(mw, weight=normal_weight, size=bigger_size, family=normal_font)
        self.bigbold: Font = Font(mw, weight=bold_weight, size=bigger_size, family=normal_font)
        self.fixed: Font = Font(mw, weight=bold_weight, size=my_size + 1, family=fixed_font)
        self.small: Font = Font(mw, weight=normal_weight, size=my_size - 2, family=normal_font)


colours: TkColours = TkColours()
fonts: Optional[TkFonts] = None


def get_fonts_and_colours():
    return colours, fonts


def set_default_fonts(mw: Tk, font_size: Optional[int] = DEFAULT_FONT_SIZE):
    global fonts
    mw.configure(background=colours.WorkspaceColour)

    if font_size is None:
        font_size = DEFAULT_FONT_SIZE
    fonts = TkFonts(mw, font_size)
    mw.option_add("*Font", fonts.normal, )
    return fonts

def set_default_fonts_and_colours(mw: Tk, font_size: Optional[int] = DEFAULT_FONT_SIZE, invert: bool = False):
    global fonts
    global colours
    colours = TkColours(mw, invert=invert)
    mw.configure(background=colours.WorkspaceColour)

    if font_size is None:
        font_size = DEFAULT_FONT_SIZE
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

    style = ttk.Style(mw)
    style.theme_use("classic")
    set_treeview_style(mw, style)


def set_treeview_style(root: Tk, style):
    """style the Treeview"""
    # https://stackoverflow.com/questions/61280744/tkinter-how-to-adjust-treeview-indentation-size-and-indicator-arrow-image
    global img_open, img_close, img_empty


    size = 15
    if fonts is not None:
        size = 2 + fonts.normal.actual("size")


    # custom indicator images
    im_open = Image.new('RGBA', (size, size), colours.DataBackground)
    im_empty = Image.new('RGBA', (size, size), colours.DataBackground)
    draw = ImageDraw.Draw(im_open)
    draw.polygon([(0, 4), ((size - 1), 4), (int(size / 2), size - 4)],
                 fill=colours.DataForeground, outline=colours.DataForeground)
    im_close = im_open.rotate(90)

    img_open = ImageTk.PhotoImage(im_open, name='img_open', master=root)
    img_close = ImageTk.PhotoImage(im_close, name='img_close', master=root)
    img_empty = ImageTk.PhotoImage(im_empty, name='img_empty', master=root)

    # colours
    style.map("Treeview",
              background=[("selected", colours.SelectedBackground),("!selected", colours.DataBackground)],
              foreground=[("selected", colours.SelectedForeground),("!selected", colours.DataForeground)],
              fieldbackground="pink")

    # custom indicator
    style.element_create('Treeitem.myindicator',
                         'image', 'img_close', ('user1', '!user2', 'img_open'), ('user2', 'img_empty'),
                         sticky='w', width=15)

    # replace Treeitem.indicator by custom one
    style.layout('Treeview.Item',
                 [('Treeitem.padding',
                   {'sticky': 'nswe',
                    'children': [('Treeitem.myindicator', {'side': 'left', 'sticky': ''}),
                                 ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                                 ('Treeitem.focus',
                                  {'side': 'left',
                                   'sticky': '',
                                   'children': [('Treeitem.text', {'side': 'left', 'sticky': ''})]})]})]
                 )


def _option_add(mw: Tk, option: str, new_value):
    """Sets the provided option on mw. If new_value is none, does nothing"""
    if new_value:
        mw.option_add(option, new_value)
