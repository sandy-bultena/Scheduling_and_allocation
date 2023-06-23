from functools import partial
from tkinter import *
from os import path
import sys


sys.path.append(path.dirname(path.dirname(__file__) + "/../../"))
from schedule.UsefulClasses.NoteBookPageInfo import NoteBookPageInfo
from schedule.GUI.MainPageBaseTk import MainPageBaseTk
from schedule.UsefulClasses.MenuItem import MenuItem, MenuType, ToolbarItem
from schedule.UsefulClasses.Preferences import Preferences

# TODO: write test for update_for_new_schedule_and_show_page

def main():
    # create the top-level window with menu, _toolbar and status bar

    main_page = MainPageBaseTk('My App', Preferences())
    (buttons, toolbar_info, menu_details) = define_inputs()
    main_page.create_menu_and_toolbars(buttons, toolbar_info, menu_details)
    filename: StringVar = StringVar()
    main_page.create_status_bar(filename)

    filename.set("This file name should appear in the status bar")

    # create the front page with _logo
    option_frame = main_page.create_front_page_base()

    # define what the _notebook pages are supposed to look like on the standard page
    notebook_info = get_notebook_info()

    # add a button so that we can switch to the 'standard page'
    Button(option_frame, text="Goto Standard Page", height=5, width=50, command=partial(switch_to_notebook, main_page, notebook_info)) \
        .pack(side='top', fill='y', expand=0)

    main_page.define_exit_callback(lambda *_: print("Application exited"))

    main_page.start_event_loop()


def get_notebook_info():
    nb1 = NoteBookPageInfo("Schedules", event_handler=lambda *_: print("Schedules called"),
                           frame_callback=lambda *_: print("Schedules frame callback"))

    nb1.subpages = [
        NoteBookPageInfo("Schedules-3", lambda *_: print("Schedules/Overview/Schedules-3 called")),
        NoteBookPageInfo("Overview-3", lambda *_: print("Schedules/Overview/Overview-3 called")),
        NoteBookPageInfo("Courses-3", lambda *_: print("Schedules/Overview/Courses-3 called")),
        NoteBookPageInfo("Teachers-3", lambda *_: print("Schedules/Overview/Teachers-3 called")),
        NoteBookPageInfo("Labs-3", lambda *_: print("Schedules/Overview/Labs-3 called")),
        NoteBookPageInfo("Streams-3", lambda *_: print("Schedules/Overview/Streams-3 called")),
    ]

    return [
        nb1,
        NoteBookPageInfo("Overview", lambda *_: print("Overview called"),
                         frame_callback=lambda *_: print("Overview frame method called")),
        NoteBookPageInfo("Courses", lambda *_: print("Courses called"), frame_args={'background': 'purple'}, ),
        NoteBookPageInfo("Teachers", lambda *_: print("Teachers called")),
        NoteBookPageInfo("Labs", lambda *_: print("Labs called")),
        NoteBookPageInfo("Streams", lambda *_: print("Streams called"))
    ]


def switch_to_notebook(main_page: MainPageBaseTk, notebook_info, *args):
    print(*args)
    main_page.create_standard_page(notebook_info)

    # main_page.bind_dirty_flag()


# def view_streams(f):
#    Button(f, text="View Streams tab", command=partial(main_page.update_for_new_schedule_and_show_page, 5)) \
#        .pack(side='top', fill='y', expand=0)


# =================================================================================================
# Setup
# =================================================================================================
def define_inputs():
    menu_items = list()

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

    # pdf sub-menu_times
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Teacher Schedules',
                                command=lambda *_: print("'Print/Teacher Schedules' selected")))
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Lab Schedules',
                                command=lambda *_: print("'Print/Lab Schedules' selected")))
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Stream Schedules',
                                command=lambda *_: print("'Print/Stream Schedules' selected")))

    pdf_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Text Output',
                                command=lambda *_: print("'Print/Text Output' selected")))

    # latex sub menu_times
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
    # _toolbar
    # -----------------------------------------------------------------------------------------
    toolbar_info = dict()
    toolbar_info['new'] = ToolbarItem(command=MenuItem.all_menu_items['new'].command, hint='Create new Schedule File')
    toolbar_info['open'] = ToolbarItem(command=MenuItem.all_menu_items['open'].command, hint='Open Schedule File')
    toolbar_info['save'] = ToolbarItem(command=MenuItem.all_menu_items['save'].command, hint='Save Schedule File')
    toolbar_order = ['new', 'open', '', 'save']

    # return list of top level menu_times items
    menu_items.append(file_menu)
    menu_items.append(print_menu)

    return toolbar_order, toolbar_info, menu_items

main()