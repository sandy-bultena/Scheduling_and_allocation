from __future__ import annotations

import platform
import typing
from functools import partial

from tkinter.ttk import Notebook
from tkinter import *
from tkinter.messagebox import showerror, showinfo, askyesnocancel

from schedule.Tk import FindImages
from ..GUI.FontsAndColoursTk import FontsAndColoursTk
from ..Presentation import globals
from ..PerlLib import Colour
from ..GUI.MenuAndToolBarTk import generate_menu, make_toolbar
from ..UsefulClasses.NoteBookPageInfo import NoteBookPageInfo
from ..Presentation.MenuItem import MenuItem, ToolbarItem

Operating_system = platform.system().lower()

MAIN_FRAME_HEIGHT = 400
MAIN_FRAME_WIDTH = 800
WELCOME_WIDTH = 600
WELCOME_HEIGHT = 600


class MainPageBaseTk:
    """Generic main page for Scheduler and Allocation Manager apps"""

    def __init__(self):
        self.logo: PhotoImage | None = None
        self.front_page_frame: Frame | None = None
        self.colours: typing.TypedDict[str, str] | None = None
        self.fonts: typing.TypedDict[str, font.Font] = None
        self.frame: Frame | None = None
        self.mw: Toplevel | None = None
        self.toolbar = None
        self.exit_callback: callable = lambda *_: {}
        self.dirty_flag_text: StringVar = StringVar(value="")
        self.pages = dict()

    def start_event_loop(self):
        """start the Tk event main event loop"""
        self.mw.mainloop()

    def define_exit_callback(self, exit_cmd=lambda *_: {}):
        """If defined, exit callback will be executed just prior to the call to 'exit'"""
        self.exit_callback = exit_cmd

    def create_main_window(self, title='Main Window'):
        """Create the main window, specify fonts and colours, creates self.frame in which to add specific widgets"""
        # create main window and frames
        self.mw = Tk()
        self.mw.title(title)
        self.frame = Frame(self.mw, height=MAIN_FRAME_HEIGHT)
        self.frame.pack(side='left')
        self.mw.geometry(f"{WELCOME_HEIGHT}x{WELCOME_WIDTH}")

        # when clicking the 'x' in the corner of the window, call _exit_schedule
        self.mw.protocol("WM_DELETE_WINDOW", self._exit_schedule)

        # colours and fonts
        FontsAndColoursTk.setup(self.mw)
        self.fonts = FontsAndColoursTk.fonts
        self.colours = FontsAndColoursTk.colours

        # bind the change to the global dirty flag
        globals.dirty_flag_changed_cb = lambda: self.dirty_flag_text.set("NOT SAVED" if globals.is_data_dirty() else "")

    def create_menu_and_toolbars(self, buttons: list[str], actions: dict[str:ToolbarItem],
                                 menu_details: list[MenuItem]):
        """Given the menu specifics, the buttons, and toolbar items, create menu and toolbar for this app"""
        # create menu
        menu_bar = Menu(self.mw)
        generate_menu(self.mw, menu_details, menu_bar)
        self.mw.configure(menu=menu_bar)

        # create toolbar
        self.toolbar = make_toolbar(self.mw, buttons, actions)
        self.toolbar.pack(side='top', expand=0, fill='x')

    def create_status_bar(self, current_filename: StringVar = None):
        """Create a status bar for current filename and dirty flag"""
        mw = self.mw
        if not current_filename:
            current_filename = StringVar()

        # choose what colour to show dirty flag text based on WorkspaceColour
        red = "#880000" if Colour.is_light(self.colours['WorkspaceColour']) else '#ff0000'

        # draw frame and labels for current filename and dirty flag
        status_frame = Frame(mw, borderwidth=0, relief='flat')
        status_frame.pack(side='bottom', expand=0, fill='x')

        Label(status_frame, textvariable=current_filename, borderwidth=1, relief='ridge') \
            .pack(side='left', expand=1, fill='x')

        Label(status_frame, textvariable=self.dirty_flag_text, borderwidth=1, relief='ridge', width=15, foreground=red) \
            .pack(side='right', fill='x')

    def create_front_page(self, logo):
        """Creates the very first page that is shown to the user"""
        mw = self.mw
        self.front_page_frame = Frame(mw, borderwidth=10, relief='flat', background=self.colours['DataBackground'])
        self.front_page_frame.pack(side='top', expand=1, fill='both')
        if not logo:
            logo = FindImages.get_logo()

        # create an image object of the logo
        self.logo = PhotoImage(file=logo)

        # frame and label
        Label(self.front_page_frame, image=self.logo, borderwidth=5, relief='flat') \
            .pack(side='left', expand=0)

        # --------------------------------------------------------------
        # frame for holding buttons for starting the scheduling tasks
        # --------------------------------------------------------------
        option_frame = Frame(self.front_page_frame, bg=self.colours['DataBackground'], borderwidth=10, relief='flat')
        option_frame.pack(side='left', expand=1, fill='both')

        Frame(option_frame, bg=self.colours['DataBackground']).pack(expand=1, fill='both')
        center_frame = Frame(option_frame, bg=self.colours['DataBackground'])
        center_frame.pack(expand=0, fill='both')
        Frame(option_frame, bg=self.colours['DataBackground']).pack(expand=1, fill='both')

        return center_frame

    def _create_standard_page(self):
        """Create the 'normal' page after the main page has fulfilled its purpose"""

        def tab_changed(notebook: Notebook, cmds: dict, *_):
            index = notebook.index(notebook.select())

            # if not set, default to empty lambda. if set and not None, call
            f = cmds.get(index, lambda *_: {})
            if f is not None:
                f()

        def create_notebook(parent: Notebook, events: dict, pages: dict[str, Frame], tabs: list[NoteBookPageInfo],
                            id_prefix: str = "", ):
            for info in tabs:
                info.panel = Frame(self.mw, **info.frame_args)
                parent.add(info.panel, text=info.name)
                i = parent.index(info.panel)
                events[i] = info.handler
                pages[id_prefix + str(i)] = info.panel
                info.id = id_prefix + str(i)

                if info.subpages:
                    sub_page_frame = Notebook(info.panel)
                    sub_page_frame.pack(expand=1, fill='both')
                    sub_events = dict()
                    create_notebook(sub_page_frame, sub_events, pages, info.subpages, f"{i}-")

                if info.frame_callback: info.frame_callback(info.panel)
            parent.bind("<<NotebookTabChanged>>", partial(tab_changed, parent, events))

        mw = self.mw
        # my @caller = caller()

        # frame and label
        (main_page_frame := Frame(mw, borderwidth=1, relief='ridge')) \
            .pack(side='top', expand=1, fill='both')

        # create notebook
        self.notebook = Notebook(main_page_frame)
        self.notebook.pack(expand=1, fill='both')

        # View page
        if not hasattr(self, 'required_notebook_tabs') or not self.required_notebook_tabs:
            raise ValueError("Error: Cannot work unless notebook tabs are defined")

        # NOTE: A LOT OF DIFFERENCES FROM PERL/TK NOTEBOOK
        # No raisecmd, so callbacks are stored in a dict and called using virtual events
        # No tab ID system, tabs are identified by their index; index is stored in
        # NoteBookPageInfo object
        # Notebook.add doesn't create a Frame, it needs to be passed in
        self.notebook_events = dict()
        create_notebook(self.notebook, self.notebook_events, self.pages, self.required_notebook_tabs)

    def define_notebook_tabs(self, notebook_tabs: list[NoteBookPageInfo]):
        self.required_notebook_tabs = notebook_tabs

    def get_notebook_page(self, page_id: int) -> NoteBookPageInfo:
        return self.pages[page_id]

    def update_for_new_schedule_and_show_page(self, default_page_id: int):
        """Reset the GUI when a new schedule is read.

           default_page_id must be the integer ID of a TOP-LEVEL notebook tab"""
        if hasattr(self, 'notebook') and self.notebook:
            already_shown = self.notebook.index(self.notebook.select()) == default_page_id
            self.notebook.select(default_page_id)

            # cmd isn't invoked if page is already shown
            # call it anyways
            if already_shown and (f := self.notebook_events.get(default_page_id, lambda *_: {})) is not None: f()
        else:
            self.front_page_frame.pack_forget()
            self._create_standard_page()

    # does this need to be implemented?
    def choose_existing_file(self, curr_dir, file_types):
        raise NotImplementedError()

    def show_error(self, title, message):
        showerror(title, message)

    # does this need to be implemented?
    def choose_file(self, curr_dir, file_types):
        raise NotImplementedError()

    def show_info(self, title, message):
        showinfo(title, message)

    def question(self, title, message):
        return askyesnocancel(title, message)

    def wait_for_it(self, title, msg):
        self.stop_waiting()

        self.wait = self.mw.winfo_toplevel()
        self.wait.title = title
        Label(self.wait, text=msg).pack(expand=1, fill='both')

        self.wait.geometry('300x450')
        self.mw.update()

    def stop_waiting(self):
        if hasattr(self, 'wait') and self.wait: self.wait.destroy()
        self.wait = None

    def _exit_schedule(self, *a):
        if hasattr(self, 'exit_callback') and self.exit_callback: self.exit_callback()
        self.mw.destroy()


if __name__ == "__main__":
    def switch_to_notebook():
        file.set(r"C:\Users\My User\Documents\Schedule.yaml")
        main_page.update_for_new_schedule_and_show_page(0)


    from tkinter import Button, font

    main_page = MainPageBaseTk()
    main_page.create_main_window('My App')

    # tried to keep similar to existing Perl structure, but note (for menu_details):
    # - the type & label need to be called "itemType" and "label"
    # - to underline access keys, add the "underline" argument to the given item
    # - an int that represents the index of the char to be underlined
    # - note that on Windows 10/11, "Underline Access Keys" (Win Settings) must be ON
    # to view the underline. This is not the case in Perl

    main_page.create_menu_and_toolbars(__menu_and_toolbar_info())

    option_frame = main_page.create_front_page(FindImages.get_logo())
    # in practice this is in a child class inheriting MainPageBaseTk, after super().create_front_page
    Button(option_frame, text="View Notebook tabs", command=switch_to_notebook) \
        .pack(side='top', fill='y', expand=0)

    main_page.create_status_bar(file := StringVar())

    main_page.bind_dirty_flag()


    def view_streams(f):
        Button(f, text="View Streams tab", command=partial(main_page.update_for_new_schedule_and_show_page, 5)) \
            .pack(side='top', fill='y', expand=0)


    # NOTE: The event_handler method is called on every first subpage, even if it's not visible, as it's selected by default
    main_page.define_notebook_tabs([
        NoteBookPageInfo("Schedules", lambda *_: print("Schedules called"), [
            NoteBookPageInfo("Schedules-2", lambda *_: print("Schedules/Schedules-2 called"), []),
            NoteBookPageInfo("Overview-2", lambda *_: print("Schedules/Overview-2 called"), [
                NoteBookPageInfo("Schedules-3", lambda *_: print("Schedules/Overview/Schedules-3 called"), []),
                NoteBookPageInfo("Overview-3", lambda *_: print("Schedules/Overview/Overview-3 called"), []),
                NoteBookPageInfo("Courses-3", lambda *_: print("Schedules/Overview/Courses-3 called"), []),
                NoteBookPageInfo("Teachers-3", lambda *_: print("Schedules/Overview/Teachers-3 called"), []),
                NoteBookPageInfo("Labs-3", lambda *_: print("Schedules/Overview/Labs-3 called"), []),
                NoteBookPageInfo("Streams-3", lambda *_: print("Schedules/Overview/Streams-3 called"), []),
            ], frame_callback=view_streams),
            NoteBookPageInfo("Courses-2", lambda *_: print("Schedules/Courses-2 called"), []),
            NoteBookPageInfo("Teachers-2", lambda *_: print("Schedules/Teachers-2 called"), []),
            NoteBookPageInfo("Labs-2", lambda *_: print("Schedules/Labs-2 called"), []),
            NoteBookPageInfo("Streams-2", lambda *_: print("Schedules/Streams-2 called"), []),
        ], frame_callback=view_streams),
        NoteBookPageInfo("Overview", lambda *_: print("Overview called"), [], frame_callback=view_streams),
        NoteBookPageInfo("Courses", lambda *_: print("Courses called"), [], frame_args={'background': 'purple'},
                         frame_callback=view_streams),
        NoteBookPageInfo("Teachers", lambda *_: print("Teachers called"), [], frame_callback=view_streams),
        NoteBookPageInfo("Labs", lambda *_: print("Labs called"), [], frame_callback=view_streams),
        NoteBookPageInfo("Streams", lambda *_: print("Streams called"), [], frame_callback=view_streams)
    ])

    main_page.define_exit_callback(lambda *_: print("Application exited"))

    main_page.start_event_loop()
