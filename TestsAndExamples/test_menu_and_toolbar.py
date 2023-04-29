import sys
import platform

sys.path.append("..")

from tkinter import *
from schedule.Presentation.MenuItem import MenuItem, MenuType, ToolbarItem
from schedule.GUI.MenuAndToolBarTk import make_toolbar, generate_menu


# =================================================================================================
# Test the GUI menu and toolbar creation work as required
# =================================================================================================


def main():
    mw = Tk()

    # preparation
    (buttons, toolbar_info, menu_details) = define_inputs()

    menu_bar = Menu(mw,name='apple')
    generate_menu(mw, menu_details, menu_bar)
    mw.configure(menu=menu_bar)

    # action
    toolbar = make_toolbar(mw, buttons, toolbar_info)
    toolbar.pack(side='top', expand=0, fill='x')
    toolbar2 = make_toolbar(mw, buttons, toolbar_info, colours={'WorkspaceColour': 'blue', 'ActiveBackground': 'pink'})
    toolbar2.pack(side='top', expand=0, fill='x')

    # test (manually)
    Label(mw, anchor='w', text="").pack()
    Label(mw, anchor='w', text="").pack()
    Label(mw, anchor='w', text= "Verify that there are TWO toolbars").pack(fill='x')
    Label(mw, anchor='w', text="The top toolbar should have the same background colour has the main window").pack(fill='x')
    Label(mw, anchor='w', text="The 2nd toolbar should have a background colour of blue").pack(fill='x')
    Label(mw, anchor='w', text="The 2nd toolbar buttons should turn pink if mouse if hovered over the button").pack(fill='x')
    Label(mw, anchor='w', text="*** KNOWN BUG: hoverbg does not work in Tk/Toolbar.py").pack(fill='x')
    Label(mw, text="").pack()
    Label(mw, anchor='w', text='Verify that there are two file menu items, "file" and "print"').pack(fill='x')
    Label(mw, anchor='w', text='Verify that "file" has "New", "Open", "Save", "Save As", "Exit"').pack(fill='x')
    Label(mw, anchor='w', text='Verify that "print" has two sub-menus "pdf" and "latex"').pack(fill='x')
    Label(mw, anchor='w', text='Verify the "pdf" and "latex" have "Teacher/Lab/Stream" menu choices').pack(fill='x')
    Label(mw, anchor='w', text="").pack(fill='x')
    Label(mw, anchor='w', text="Toolbar should have three buttons, with a '|' between open and save").pack(fill='x')
    Label(mw, anchor='w', text="").pack(fill='x')
    Label(mw, anchor='w', text="Verify that all buttons and menu items print appropriate message to console").pack(fill='x')
    Label(mw, anchor='w', text="Verify that all menu item shortcut keys work as expected").pack(fill='x')
    Label(mw, anchor='w', text="If MAC, verify that all menu item 'command'-? shortcut keys work as expected").pack(fill='x')

    mw.mainloop()


# =================================================================================================
# Setup
# =================================================================================================
def define_inputs():
    menu = list()

    # -----------------------------------------------------------------------------------------
    # File menu
    # -----------------------------------------------------------------------------------------
    file_menu = MenuItem(name='file', menu_type=MenuType.Cascade, label='File')
    file_menu.add_child(MenuItem(name='new', menu_type=MenuType.Command, label='New', accelerator='Ctrl-n',
                                 command=lambda *_: print("'File/New' selected")))
    file_menu.add_child(MenuItem(name='open', menu_type=MenuType.Command, label='Open', accelerator='Ctrl-o',
                                 command=lambda *_: print("'File/Open' selected")))

    file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    file_menu.add_child(MenuItem(name='save', menu_type=MenuType.Command, label='Save', accelerator='Ctrl-s',
                                 underline=0,
                                 command=lambda *_: print("'File/Save' selected")))
    file_menu.add_child(MenuItem(name='save_as', menu_type=MenuType.Command, label='Save As',
                                 command=lambda *_: print("'File/Save As' selected")))

    file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    file_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Exit', accelerator='Ctrl-e',
                                 command=lambda *_: print("'File/Exit' selected")))

    # -----------------------------------------------------------------------------------------
    # Print menu
    # -----------------------------------------------------------------------------------------
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

    pdf_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Text Output',
                                command=lambda *_: print("'Print/Text Output' selected")))

    # latex sub menu
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Teacher Schedules',
                                  command=lambda *_: print("'Print/Teacher Schedules' selected")))
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Lab Schedules',
                                  command=lambda *_: print("'Print/Lab Schedules' selected")))
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Stream Schedules',
                                  command=lambda *_: print("'Print/Stream Schedules' selected")))

    latex_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Text Output',
                                  command=lambda *_: print("'Print/Text Output' selected")))

    # -----------------------------------------------------------------------------------------
    # toolbar
    # -----------------------------------------------------------------------------------------
    toolbar_info = dict()
    toolbar_info['new'] = ToolbarItem(command=MenuItem.all_menu_items['new'].command, hint='Create new Schedule File')
    toolbar_info['open'] = ToolbarItem(command=MenuItem.all_menu_items['open'].command, hint='Open Schedule File')
    toolbar_info['save'] = ToolbarItem(command=MenuItem.all_menu_items['save'].command, hint='Save Schedule File')
    toolbar_order = ['new', 'open', '', 'save']

    # return list of top level menu items
    menu.append(file_menu)
    menu.append(print_menu)

    return toolbar_order, toolbar_info, menu


if __name__ == "__main__":
    main()
