# COMPLETED
from __future__ import annotations

"""
Example::

    menu = list()

    file_menu = MenuItem(name='file', menu_type=MenuType.Cascade, label='File')
    file_menu.add_child(MenuItem(name='new', menu_type=MenuType.Command, label='New', accelerator='Ctrl-n',
                                 command=lambda *_: print("'File/New' selected")))
    file_menu.add_child(MenuItem(menu_type=MenuType.Separator))
    file_menu.add_child(MenuItem(name='open', menu_type=MenuType.Command, label='Open', accelerator='Ctrl-o',
                                 command=lambda *_: print("'File/Open' selected")))

    print_menu = MenuItem(name='print', menu_type=MenuType.Cascade, label='Print')
    pdf_menu = MenuItem(menu_type=MenuType.Cascade, label='PDF')
    latex_menu = MenuItem(menu_type=MenuType.Cascade, label='Latex')
    print_menu.add_child(pdf_menu)
    print_menu.add_child(latex_menu)

    # pdf sub-menu
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Teacher Schedules',
                                command=lambda *_: print("'Print/Teacher Schedules' selected")))
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Lab Schedules',
                                command=lambda *_: print("'Print/Lab Schedules' selected")))
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Stream Schedules',
                                command=lambda *_: print("'Print/Stream Schedules' selected")))

    menu.append(file_menu)
    menu.append(print_menu)

    toolbar_info = dict()
    toolbar_info['new'] = ToolbarItem(command=MenuItem.all_menu_items['new'].command, hint='Create new Schedule File')
    toolbar_info['open'] = ToolbarItem(command=MenuItem.all_menu_items['open'].command, hint='Open Schedule File')
    toolbar_info['save'] = ToolbarItem(command=MenuItem.all_menu_items['save'].command, hint='Save Schedule File')
    toolbar_order = ['new', 'open', '', 'save']

"""


class MenuType:
    """A pseudo enum to ensure that the MenuItem type is valid"""
    Command = 'command'
    Separator = 'separator'
    Radiobutton = 'radiobutton'
    Checkbutton = 'checkbutton'
    Cascade = 'cascade'


class MenuItem:
    """Define a menu_item (type, options, etc)"""

    all_menu_items: dict[str, MenuItem] = dict()
    """a dictionary of all menu_items that were created.  Key is the 'name' property of the menu item"""

    def __init__(self, name: str = "", label: str = "", tearoff: int = 0, menu_type: MenuType = MenuType.Command,
                 accelerator: str = '', command: callable = lambda: None, underline: int = 0):
        self.label = label
        self.tearoff = tearoff
        self.menu_type = menu_type
        self.name = name
        self.accelerator = accelerator
        self.command = command
        self.children = list()
        self.underline = underline
        MenuItem.all_menu_items[self.name] = self

    def options_dict(self) -> dict[str, str]:
        """return a dictionary of options, appropriate to the menu type"""
        options = dict()
        if self.menu_type != MenuType.Separator:
            options = {'label': self.label, 'accelerator': self.accelerator,
                       'command': self.command, 'underline': self.underline}
        return options

    def add_child(self, menu_item: MenuItem):
        """add a new menu item as a sub-child of on existing menu item"""
        # TODO: Throw an exception if self MenuType is not 'cascade'
        self.children.append(menu_item)


class ToolbarItem:
    """data defining at toolbar item, command, hint, image, etc"""

    def __init__(self, command: callable | None = None, hint: str | None = None, image: str | None = None, sc=None):
        self.command = command
        self.hint = hint
        self.image = image
        self.sc = sc
