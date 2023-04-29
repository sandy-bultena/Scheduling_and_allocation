from __future__ import annotations


class MenuType:
    Command = 'command'
    Separator = 'separator'
    Radiobutton = 'radiobutton'
    Checkbutton = 'checkbutton'
    Cascade = 'cascade'


class MenuItem:
    all_menu_items: dict[str, MenuItem] = dict()

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
        options = dict()
        if self.menu_type != MenuType.Separator:
            options = {'label': self.label, 'accelerator': self.accelerator,
                       'command': self.command, 'underline': self.underline}
        return options

    def add_child(self, menu_item):
        self.children.append(menu_item)


class ToolbarItem:
    def __init__(self, command: callable | None = None, hint: str | None = None, image: str | None = None, sc=None):
        self.command = command
        self.hint = hint
        self.image = image
        self.sc = sc

