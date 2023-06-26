from __future__ import annotations

import platform
from functools import partial

from tkinter.ttk import Notebook
from tkinter import *
from tkinter.font import Font
from tkinter import filedialog as fd
from typing import Callable, Optional

# from tkinter.messagebox import showerror, showinfo, askyesnocancel

from schedule.Tk import FindImages
import schedule.Tk.InitGuiFontsAndColours as tk_fonts_and_colours
from ..Presentation import globals
from ..GUI.MenuAndToolBarTk import generate_menu, make_toolbar
from ..UsefulClasses.NoteBookPageInfo import NoteBookPageInfo
from ..UsefulClasses.MenuItem import MenuItem, ToolbarItem
import schedule.UsefulClasses.Colour as Colour
from ..UsefulClasses.Preferences import Preferences

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

    def __init__(self, title, preferences: Preferences):
        self.dark_mode = preferences.dark_mode()
        self.colours: dict[tk_fonts_and_colours.available_colours, str] | None = None
        self.fonts: dict[tk_fonts_and_colours.available_fonts, Font] | None = None
        self.exit_callback: Callable[[], None] = lambda: None
        self.dict_of_frames: dict[str, Frame] = dict()
        self._open_schedule_callback: Callable[[str, str], None] = lambda filename, semester: None
        self._new_schedule_callback: Callable[[], None] = lambda: None

        self._preferences = preferences
        self._standard_page_created: bool = False
        self._wait = None
        self._notebook_pages_info: list[NoteBookPageInfo] | None = None
        self._front_page_frame: Optional[Frame] = None
        self._mw: Optional[Toplevel] = None
        self._toolbar = None
        self._default_notebook_page: int = 0
        self._top_level_notebook: Optional[Notebook] = None

        self._initialize_top_window(title)
        self._dirty_flag_text: StringVar = StringVar(value="")
        self._schedule_filename: StringVar = StringVar(value="")

    @property
    def schedule_filename(self):
        return self._schedule_filename.get()

    @schedule_filename.setter
    def schedule_filename(self, value: str):
        self._schedule_filename.set(value)

    def create_menu_and_toolbars(self, buttons: list[str], toolbar_info: dict[str:ToolbarItem],
                                 menu_details: list[MenuItem]):

        """Given the menu specifics, the buttons, and _toolbar items, create menu and _toolbar for this app"""
        # create menu
        menu_bar = Menu(self._mw)
        generate_menu(self._mw, menu_details, menu_bar)
        self._mw.configure(menu=menu_bar)

        # create _toolbar
        self._toolbar = make_toolbar(self._mw, buttons, toolbar_info)
        self._toolbar.pack(side='top', expand=0, fill='x')

    def create_status_bar(self):
        """Create a status bar for current filename and dirty flag"""
        mw = self._mw

        # choose what colour to show dirty flag text based on WorkspaceColour
        red = "#880000" if Colour.is_light(self.colours['WorkspaceColour']) else '#ff0000'

        # draw frame and labels for current filename and dirty flag
        status_frame = Frame(mw, borderwidth=0, relief='flat')
        status_frame.pack(side='bottom', expand=0, fill='x')

        Label(status_frame, textvariable=self._schedule_filename, borderwidth=1, relief='ridge') \
            .pack(side='left', expand=1, fill='x')

        Label(status_frame, textvariable=self._dirty_flag_text, borderwidth=1, relief='ridge', width=15,
              foreground=red).pack(side='right', fill='x')

    def create_front_page_base(self, logo: PhotoImage | None = None):
        """Creates the very first page that is shown to the user"""
        mw = self._mw
        self._front_page_frame = Frame(mw, borderwidth=10, relief='flat', background=self.colours['DataBackground'])
        self._front_page_frame.pack(side='top', expand=1, fill='both')
        if logo is None:
            logo = FindImages.get_logo()

        # create an image object of the _logo
        # ... for some weird reason, if logo is not part of 'self', then it doesn't work
        # Weird, right?
        self.logo = PhotoImage(file=logo)

        # frame and label
        Label(self._front_page_frame, image=self.logo, borderwidth=5, relief='flat') \
            .pack(side='left', expand=0)

        # --------------------------------------------------------------
        # frame for holding buttons for starting the scheduling tasks
        # --------------------------------------------------------------
        option_frame = Frame(self._front_page_frame, bg=self.colours['DataBackground'], borderwidth=10, relief='flat')
        option_frame.pack(side='left', expand=1, fill='both')

        Frame(option_frame, bg=self.colours['DataBackground']).pack(expand=1, fill='both')
        center_frame = Frame(option_frame, bg=self.colours['DataBackground'])
        center_frame.pack(expand=0, fill='both')
        Frame(option_frame, bg=self.colours['DataBackground']).pack(expand=1, fill='both')

        return center_frame

    def create_standard_page(self, notebook_pages_info: list[NoteBookPageInfo] | None = None):
        """Create the 'normal' page after the main page has fulfilled its purpose"""

        # if the page is already created, do not recreate it
        if self._standard_page_created:
            if self._top_level_notebook:
                self._top_level_notebook.select(self._default_notebook_page)
                self._top_level_notebook.event_generate("<<NotebookTabChanged>>")
                return

        # create the page
        self._standard_page_created = True
        mw = self._mw
        self._front_page_frame.destroy()

        # frame
        main_page_frame = Frame(mw, borderwidth=1, relief='ridge')
        main_page_frame.pack(side='top', expand=1, fill='both')

        self._notebook_pages_info = notebook_pages_info

        # Add notebooks if required
        if self._notebook_pages_info:
            notebook = Notebook(main_page_frame)
            notebook.pack(expand=1, fill='both')
            self._top_level_notebook = notebook
            self.dict_of_frames = self._create_notebook_pages(notebook, self._notebook_pages_info)

    def start_event_loop(self):
        """start the Tk event main event loop"""
        self._mw.mainloop()

    def define_exit_callback(self, exit_cmd=lambda *_: {}):
        """If defined, exit callback will be executed just prior to the call to 'exit'"""
        self.exit_callback = exit_cmd

    def _initialize_top_window(self, title):
        """Create the top level window, specify fonts and colours"""
        # create main window and frames
        self._mw = Tk()
        self._mw.title(title)
        self._mw.geometry(f"{WELCOME_HEIGHT}x{WELCOME_WIDTH}")

        # when clicking the 'x' in the corner of the window, call _exit_schedule
        self._mw.protocol("WM_DELETE_WINDOW", self._exit_schedule)

        # colours and fonts
        tk_fonts_and_colours.set_default_fonts_and_colours(self._mw, dark_mode=self.dark_mode)
        self.colours = tk_fonts_and_colours.colours
        self.fonts = tk_fonts_and_colours.fonts

        # bind the change to the global dirty flag
        globals.dirty_flag_changed_cb = lambda: self._dirty_flag_text.set(
            "NOT SAVED" if globals.is_data_dirty() else "")

    def _create_notebook_pages(self, notebook: Notebook, pages_info: list[NoteBookPageInfo],
                               ) -> dict[str, Frame]:
        """
        create Notebook with specified pages described by pages_info
        :param notebook: Notebook object
        :param pages_info: information about how we want the page to look
        :return: a dictionary of frames contained within each Notebook tab

        """
        events: dict[int, callable] = dict()
        pages: dict[str, Frame] = dict()

        for info in pages_info:
            frame = Frame(self._mw, **info.frame_args)
            notebook.add(frame, text=info.name)
            i = notebook.index(frame)
            events[i] = info.handler if info.handler else lambda *_: {}
            pages[info.name.lower()] = frame
            if info.is_default_page:
                self._default_notebook_page = i

            if info.subpages:
                sub_page_frame = Notebook(frame)
                sub_page_frame.pack(expand=1, fill='both')
                sub_pages = self._create_notebook_pages(sub_page_frame, info.subpages)
                pages.update(sub_pages)

            if info.frame_callback:
                info.frame_callback(info.name.lower())

        # add the binding for changing of events, and include a list of events for each tab change
        notebook.bind("<<NotebookTabChanged>>", partial(_tab_changed, notebook, events))

        return pages

    # def update_for_new_schedule_and_show_page(self):
    #     """Reset the GUI when a new schedule is read."""
    #
    #     if self._standard_page_created:
    #         if self._top_level_notebook:
    #             self._top_level_notebook.select(self._default_notebook_page)
    #             self._top_level_notebook.event_generate("<<NotebookTabChanged>>")
    #     else:
    #         self.create_standard_page()

    def wait_for_it(self, title, msg):
        self.stop_waiting()

        self._wait = self._mw.winfo_toplevel()
        self._wait.title = title
        Label(self._wait, text=msg).pack(expand=1, fill='both')

        self._wait.geometry('300x450')
        self._mw.update()

    def stop_waiting(self):
        if self._wait:
            self._wait.destroy()
        self._wait = None

    def _exit_schedule(self, *_):
        self.exit_callback()
        self._mw.destroy()

    # ========================================================================
    # choose existing file to read
    # ========================================================================
    def select_file(self) -> Optional[str]:
        current_dir = self._preferences.current_dir()
        filetypes = (
            ('schedule files', '*.csv'),
            ('All files', '*.*')
        )
        if current_dir is None:
            current_dir = self._preferences.home_directory()
        if current_dir is not None:
            filename = fd.askopenfilename(
                title='Open a file for ' + self._preferences.semester(),
                initialdir=current_dir,
                filetypes=filetypes
            )
        else:
            filename = fd.askopenfilename(
                title='Open a file',
                filetypes=filetypes
            )
        return filename
    
    # ========================================================================
    # read_current_file
    # ========================================================================
    def _open_schedule(self):
        semester = self._preferences.semester()
        current_file = self._preferences.current_file()
        if current_file is not None:
            self._open_schedule_callback(current_file, semester)
