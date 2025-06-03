from tkinter import *
import re
from os import path

from schedule.Tk.MenuItem import MenuItem, MenuType, ToolbarItem
from ..Tk import FindImages
from ..Tk.ToolBar import ToolBar
import schedule.Tk.InitGuiFontsAndColours as fas


"""
Example::

    from tkinter import *
    from schedule.Presentation.MenuItem import MenuItem, MenuType, ToolbarItem
    from schedule.GUI_Pages.MenuAndToolBarTk import make_toolbar, generate_menu

    _mw = Tk()

    (buttons, toolbar_info, menu_details) = define_inputs()

    menu_bar = Menu(_mw)
    generate_menu(_mw, menu_details, menu_bar)
    _mw.configure(menu=menu_bar)

    _toolbar = make_toolbar(_mw, buttons, toolbar_info)
    _toolbar.pack(side='top', expand=0, fill='x')

    _mw.mainloop()

    def define_inputs():
        menu = list()
    
        file_menu = MenuItem(name='file', menu_type=MenuType.Cascade, label='File')
        file_menu.add_child(MenuItem(name='new', menu_type=MenuType.Command, label='New', accelerator='Ctrl-n',
                                     command=lambda *_: print("'File/New' selected")))
        file_menu.add_child(MenuItem(name='open', menu_type=MenuType.Command, label='Open', accelerator='Ctrl-o',
                                     command=lambda *_: print("'File/Open' selected")))
        file_menu.add_child(MenuItem(name='save', menu_type=MenuType.Command, label='Save', accelerator='Ctrl-s',
                                     underline=0,
                                     command=lambda *_: print("'File/Save' selected")))

        toolbar_info = dict()
        toolbar_info['new'] = ToolbarItem(command=MenuItem.all_menu_items['new'].command, hint='New Schedule File')
        toolbar_info['open'] = ToolbarItem(command=MenuItem.all_menu_items['open'].command, hint='Open Schedule File')
        toolbar_info['save'] = ToolbarItem(command=MenuItem.all_menu_items['save'].command, hint='Save Schedule File')
        toolbar_order = ['new', 'open', '', 'save']
    
        menu.append(file_menu)
        menu.append(print_menu)
    
        return toolbar_order, toolbar_info, menu
    
"""


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
                 colours: fas.TkColours = fas.TkColours()) -> ToolBar:
    """Create a _toolbar described by the actions"""
    image_dir = FindImages.get_image_dir()
    bg_colour = colours.WorkspaceColour
    ab_colour = colours.ActiveBackground
    toolbar = ToolBar(mw, buttonbg=bg_colour, hoverbg=ab_colour)

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
