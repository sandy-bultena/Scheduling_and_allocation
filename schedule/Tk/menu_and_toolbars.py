from __future__ import annotations
from tkinter import *
from dataclasses import dataclass, field
from typing import Callable, Optional, ClassVar, Any
from enum import Enum

import re
from os import path
from . import FindImages
from .ToolBar import ToolBar
from .InitGuiFontsAndColours import TkColours


class MenuType(Enum):
    """ensure that the MenuItem resource_type is valid"""
    Command = 'command'
    Separator = 'separator'
    Radiobutton = 'radiobutton'
    Checkbutton = 'checkbutton'
    Cascade = 'cascade'


@dataclass
class MenuItem:
    """Define a menu_item (resource_type, options, etc)"""

    # a dictionary of all menu_items that were created.  Key is the 'name' property of the menu item
    all_menu_items: ClassVar[dict[str, MenuItem]] = {}

    label: str = ""
    tear_off: bool = 0
    menu_type: MenuType = MenuType.Command
    name: str = ""
    accelerator: str = ""
    command: Callable = lambda *_: None
    children: list[MenuItem] = field(default_factory=list)
    underline: bool = False

    def __post_init__(self):
        MenuItem.all_menu_items[self.name] = self

    def options_dict(self) -> dict[str, str]:
        """return a dictionary of options, appropriate to the menu resource_type"""
        options = dict()
        if self.menu_type != MenuType.Separator:
            options = {'label': self.label, 'accelerator': self.accelerator,
                       'command': self.command, 'underline': self.underline}
        return options

    def add_child(self, menu_item: MenuItem):
        """add a new menu item as a sub-child of on existing menu item"""

        # if self is not a cascade resource_type menu item, then it should not have
        # children (i.e. non-cascade menu-items should not be parents)
        if self.menu_type != MenuType.Cascade:
            msg = f"Menu '{self.name}' is of resource_type '{self.menu_type}' and cannot support children"
            raise TypeError(msg)

        # procreate
        self.children.append(menu_item)


@dataclass
class ToolbarItem:
    """data defining a _toolbar item, command, hint, image, etc"""
    command: Optional[Callable] = lambda *_: None
    hint: Optional[str] = None
    image: Optional[str] = None


def generate_menu(mw, menu_details: Optional[list[MenuItem]], parent: Menu):
    """Create a gui menu bar based off of the menu_details"""

    if menu_details is None:
        return
    
    for menu_item in menu_details:

        # Cascading menu
        if menu_item.menu_type == MenuType.Cascade:
            new_menu = Menu(parent, tearoff=menu_item.tear_off)
            generate_menu(mw, menu_item.children, new_menu)
            parent.add_cascade(label=menu_item.label, menu=new_menu)

        # simple separator
        elif menu_item.menu_type == MenuType.Separator:
            parent.add_separator()

        # button or command or radiobutton or...
        else:
            options: dict = menu_item.options_dict()
            parent.add(menu_item.menu_type.value, **options)

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
                 colours: TkColours = TkColours(), **kwargs) -> ToolBar:
    """Create a _toolbar described by the actions"""
    image_dir = FindImages.get_image_dir()
    toolbar = ToolBar(mw, colours, **kwargs)

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
