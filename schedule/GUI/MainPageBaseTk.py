from __future__ import annotations

import platform
from functools import partial

from tkinter.ttk import Notebook
from tkinter import *
from tkinter.font import Font

# from tkinter.messagebox import showerror, showinfo, askyesnocancel

from schedule.Tk import FindImages
import schedule.Tk.InitGuiFontsAndColours as tk_fonts_and_colours
from ..Presentation import globals
from ..GUI.MenuAndToolBarTk import generate_menu, make_toolbar
from ..UsefulClasses.NoteBookPageInfo import NoteBookPageInfo
from ..UsefulClasses.MenuItem import MenuItem, ToolbarItem
import schedule.UsefulClasses.Colour as Colour

Operating_system = platform.system().lower()

MAIN_FRAME_HEIGHT = 400
MAIN_FRAME_WIDTH = 800
WELCOME_WIDTH = 600
WELCOME_HEIGHT = 600


def _tab_changed(notebook: Notebook, events: dict, *_):
    """calls the appropriate callback when the tab has changed"""
    index = notebook.index(notebook.select())
    f = events.get(index, lambda *_: {})
    f()


class MainPageBaseTk:
    """Generic main page for Scheduler and Allocation Manager apps"""

    def __init__(self, title="Main Window"):
        self.notebook: Notebook | None = None
        self.wait = None
        self.notebook_pages_info: list[NoteBookPageInfo] | None = None
        self.logo: PhotoImage | None = None
        self.front_page_frame: Frame | None = None
        self.colours: dict[tk_fonts_and_colours.available_colours, str] | None = None
        self.fonts: dict[tk_fonts_and_colours.available_fonts, Font] | None = None
        self.frame: Frame | None = None
        self.mw: Toplevel | None = None
        self.toolbar = None
        self.exit_callback: callable = lambda *_: {}
        self.pages = dict()

        self._initialize_top_window(title)
        self.dirty_flag_text: StringVar = StringVar(value="")

    def create_menu_and_toolbars(self, buttons: list[str], toolbar_info: dict[str:ToolbarItem],
                                 menu_details: list[MenuItem]):

        """Given the menu specifics, the buttons, and toolbar items, create menu and toolbar for this app"""
        # create menu
        menu_bar = Menu(self.mw)
        generate_menu(self.mw, menu_details, menu_bar)
        self.mw.configure(menu=menu_bar)

        # create toolbar
        self.toolbar = make_toolbar(self.mw, buttons, toolbar_info)
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

        Label(status_frame, textvariable=self.dirty_flag_text, borderwidth=1, relief='ridge', width=15,
              foreground=red).pack(side='right', fill='x')

    def create_front_page(self, logo: PhotoImage | None = None):
        """Creates the very first page that is shown to the user"""
        mw = self.mw
        self.front_page_frame = Frame(mw, borderwidth=10, relief='flat', background=self.colours['DataBackground'])
        self.front_page_frame.pack(side='top', expand=1, fill='both')
        if logo is None:
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

    def create_standard_page(self, notebook_pages_info: list[NoteBookPageInfo] | None = None):
        """Create the 'normal' page after the main page has fulfilled its purpose"""

        mw = self.mw
        self.front_page_frame.destroy()

        # frame
        main_page_frame = Frame(mw, borderwidth=1, relief='ridge')
        main_page_frame.pack(side='top', expand=1, fill='both')

        self.notebook_pages_info = notebook_pages_info

        # Add notebooks if required
        if self.notebook_pages_info:
            self.notebook = Notebook(main_page_frame)
            self.notebook.pack(expand=1, fill='both')
            self.pages = self._create_notebook_pages(self.notebook, self.notebook_pages_info)

    def start_event_loop(self):
        """start the Tk event main event loop"""
        self.mw.mainloop()

    def define_exit_callback(self, exit_cmd=lambda *_: {}):
        """If defined, exit callback will be executed just prior to the call to 'exit'"""
        self.exit_callback = exit_cmd

    def _initialize_top_window(self, title):
        """Create the top level window, specify fonts and colours"""
        # create main window and frames
        self.mw = Tk()
        self.mw.title(title)
        self.mw.geometry(f"{WELCOME_HEIGHT}x{WELCOME_WIDTH}")

        # when clicking the 'x' in the corner of the window, call _exit_schedule
        self.mw.protocol("WM_DELETE_WINDOW", self._exit_schedule)

        # colours and fonts
        tk_fonts_and_colours.set_default_fonts_and_colours(self.mw)
        self.colours = tk_fonts_and_colours.colours
        self.fonts = tk_fonts_and_colours.fonts

        # bind the change to the global dirty flag
        globals.dirty_flag_changed_cb = lambda: self.dirty_flag_text.set("NOT SAVED" if globals.is_data_dirty() else "")

    def _create_notebook_pages(self, parent: Notebook, pages_info: list[NoteBookPageInfo],
                               id_prefix: str = "", ) -> dict[str, Frame]:
        """
        create notebook with specified pages described by pages_info
        :param parent: notebook object
        :param pages_info: information about how we want the page to look
        :param id_prefix: adds a prefix to the page_info id
        :return: a dictionary of frames contained within each notebook tab

        """
        events: dict[int, callable] = dict()
        pages: dict[str, Frame] = dict()

        for info in pages_info:
            info.panel = Frame(self.mw, **info.frame_args)
            parent.add(info.panel, text=info.name)
            i = parent.index(info.panel)
            events[i] = info.handler if info.handler else lambda *_: {}
            pages[id_prefix + str(i)] = info.panel
            info.id = id_prefix + str(i)

            if info.subpages:
                sub_page_frame = Notebook(info.panel)
                sub_page_frame.pack(expand=1, fill='both')
                sub_pages = self._create_notebook_pages(sub_page_frame, info.subpages, f"{i}-")
                pages.update(sub_pages)

            if info.frame_callback:
                info.frame_callback(info.panel)

        # add the binding for changing of events, and include a list of events for each tab change
        parent.bind("<<NotebookTabChanged>>", partial(_tab_changed, parent, events))

        return pages

    def update_for_new_schedule_and_show_page(self, default_page_id: int):
        """Reset the GUI when a new schedule is read."""

        if self.notebook:
            self.notebook.select(default_page_id)
            self.notebook.event_generate("<<NotebookTabChanged>>")
        else:
            self.front_page_frame.pack_forget()
            self.create_standard_page()

    # does this need to be implemented?
    # TODO: Yes this needs to be implemented, since we have given the heave-ho on the database
    def choose_file(self, curr_dir, file_types):
        raise NotImplementedError()

    def wait_for_it(self, title, msg):
        self.stop_waiting()

        self.wait = self.mw.winfo_toplevel()
        self.wait.title = title
        Label(self.wait, text=msg).pack(expand=1, fill='both')

        self.wait.geometry('300x450')
        self.mw.update()

    def stop_waiting(self):
        if self.wait:
            self.wait.destroy()
        self.wait = None

    def _exit_schedule(self, *_):
        self.exit_callback()
        self.mw.destroy()
