from tkinter import *

import re
from os import path

from .MenuItem import MenuItem, MenuType, ToolbarItem
from . import FindImages
from .ToolBar import ToolBar
from .InitGuiFontsAndColours import TkColours


def generate_menu(mw, menu_details: list[MenuItem], parent: Menu):
    """Create a gui menu bar based off of the menu_details"""

    for menu_item in menu_details:

        # Cascading menu
        if menu_item.menu_type == MenuType.Cascade:
            new_menu = Menu(parent, tearoff=menu_item.tearoff)
            generate_menu(mw, menu_item.children, new_menu)
            parent.add_cascade(label=menu_item.label, menu=new_menu)

        # simple separator
        elif menu_item.menu_type == MenuType.Separator:
            parent.add_separator()

        # button or command or radiobutton or...
        else:
            options: dict = menu_item.options_dict()
            parent.add(menu_item.menu_type, **options)

        # bind accelerators
        if menu_item.accelerator:
            x = re.match(r'ctrl-(.)', menu_item.accelerator, re.RegexFlag.IGNORECASE)
            if x:
                binding = f"<Control-Key-{x.group(1).lower()}>"
                mw.bind(binding, menu_item.command)

                # if darwin, also bind the 'command' key for MAC users
                binding = f"<Command-Key-{x.group(1).lower()}>"
                mw.bind(binding, menu_item.command)


def make_toolbar(mw, button_names: list[str], actions: dict[str:ToolbarItem],
                 colours: TkColours = TkColours()) -> ToolBar:
    """Create a _toolbar described by the actions"""
    image_dir = FindImages.get_image_dir()
    toolbar = ToolBar(mw, colours)

    # create all the buttons
    for button_name in button_names:
        if not button_name:  # if button not defined, insert a divider
            toolbar.bar()
        else:
            image = actions[button_name].image if actions[button_name].image else f'{button_name}.gif'
            full_image_path = path.join(image_dir, image)
            toolbar.add(
                name=button_name,
                image=full_image_path,
                command=actions[button_name].command,
                hint=actions[button_name].hint,
            )
    return toolbar
