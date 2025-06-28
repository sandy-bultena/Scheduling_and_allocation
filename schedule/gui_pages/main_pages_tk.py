from __future__ import annotations

"""
MAIN PAGE - Gui entry point to the application(s)

- Forms base class for Scheduler and Allocation applications
"""

import platform
from functools import partial

from tkinter.ttk import Notebook
from tkinter import *
from tkinter import filedialog as fd
from typing import Optional, TYPE_CHECKING

from tkinter.messagebox import showerror, showinfo, askyesnocancel

from schedule.Tk import FindImages
from schedule.Tk import set_default_fonts_and_colours, TkColours, TkFonts
from schedule.Tk import generate_menu, make_toolbar
from ..Utilities.NoteBookPageInfo import NoteBookPageInfo
from schedule.Tk import MenuItem, ToolbarItem
from ..Utilities.Preferences import Preferences

if TYPE_CHECKING:
    pass

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
    bin_dir = None

    # ===================================================================================
    # constructor
    # ===================================================================================
    def __init__(self, title, preferences: Preferences):

        # public properties
        self.dark_mode = False
        self.colours: Optional[TkColours] = None
        self.fonts: Optional[TkFonts] = None
        self.dict_of_frames: dict[str, Frame] = dict()
        self.logo: Optional[PhotoImage] = None
        self.mw: Optional[Toplevel] = None

        # private properties
        self._preferences = preferences
        self._standard_page_created: bool = False
        self._wait = None
        self._notebook_pages_info: list[NoteBookPageInfo] | None = None
        self._front_page_frame: Optional[Frame] = None
        self._toolbar = None
        self._default_notebook_page: int = 0
        self._top_level_notebook: Optional[Notebook] = None

        # Create the Tk main window
        self._create_main_window(title)

        # set the filename so that it can be bound later
        self._status_bar_file_info: StringVar = StringVar(value="None")

        # set the dirty text so it can be bound later
        self._status_bar_dirty: StringVar = StringVar(value="")

    # ===================================================================================
    # main window
    # ===================================================================================
    def _create_main_window(self, title):
        """Create the top level window, specify fonts and colors"""
        # create main window and frames
        self.mw = Tk()
        self.mw.title(title)
        self.mw.geometry(f"{WELCOME_HEIGHT}x{WELCOME_WIDTH}")

        # when clicking the 'x' in the corner of the window, call _exit_schedule
        self.mw.protocol("WM_DELETE_WINDOW", self._exit_schedule)

        # colors and fonts
        self.colours, self.fonts = set_default_fonts_and_colours(self.mw, invert=self.dark_mode)

    def start_event_loop(self):
        """time_start the Tk event main event loop"""
        self.mw.mainloop()

    # ===================================================================================
    # properties
    # ===================================================================================
    @property
    def status_bar_file_info(self):
        return self._status_bar_file_info.get()

    @status_bar_file_info.setter
    def status_bar_file_info(self, value: str):
        self._status_bar_file_info.set(value)

    @property
    def dirty_text(self):
        return self._status_bar_dirty.get()

    @dirty_text.setter
    def dirty_text(self, value):
        self._status_bar_dirty.set(value)

    # ===================================================================================
    # menu and toolbars
    # ===================================================================================
    def create_menu_and_toolbars(self, buttons: list[str], toolbar_info: dict[str:ToolbarItem],
                                 menu_details: list[MenuItem]):

        """Given the menu specifics, the buttons, and _toolbar items, create menu and _toolbar for this app"""
        # create menu
        menu_bar = Menu(self.mw)
        generate_menu(self.mw, menu_details, menu_bar)
        self.mw.configure(menu=menu_bar)

        # create _toolbar
        self._toolbar = make_toolbar(self.mw, buttons, toolbar_info)
        self._toolbar.pack(side='top', expand=0, fill='x')

    # ===================================================================================
    # status bar
    # ===================================================================================
    def create_status_bar(self):
        """Create a status bar for current filename and dirty flag"""
        mw = self.mw

        # draw frame and labels for current filename and dirty flag
        status_frame = Frame(mw, borderwidth=0, relief='flat')
        status_frame.pack(side='bottom', expand=0, fill='x')

        Label(status_frame, textvariable=self._status_bar_file_info, borderwidth=1, relief='ridge',
              anchor='w',
              ).pack(side='left', expand=1, fill='x')

        Label(status_frame, textvariable=self._status_bar_dirty, borderwidth=1, relief='ridge', width=15,
              foreground=self.colours.DirtyColour).pack(side='right', fill='x')

    # ===================================================================================
    # front page
    # ===================================================================================
    def create_front_page_base(self, logo: PhotoImage | None = None):
        """Creates the very first page that is shown to the user"""
        mw = self.mw
        self._front_page_frame = Frame(mw, borderwidth=10, relief='flat', background=self.colours.DataBackground)
        self._front_page_frame.pack(side='top', expand=1, fill='both')
        if logo is None:
            logo = FindImages.get_logo(MainPageBaseTk.bin_dir)

        # create an image object of the _logo
        # ... for some weird reason, if logo is not part of 'self', then it doesn't work
        # Weird, right?
        self.logo = PhotoImage(file=logo)

        # frame and label
        Label(self._front_page_frame, image=self.logo, borderwidth=0, relief='flat') \
            .pack(side='left', expand=0)

        # --------------------------------------------------------------
        # frame for holding buttons for starting the scheduling tasks
        # --------------------------------------------------------------
        option_frame = Frame(
            self._front_page_frame,
            background=self.colours.DataBackground,
            borderwidth=10,
            relief='flat')
        option_frame.pack(side='left', expand=1, fill='both')

        Frame(option_frame, background=self.colours.DataBackground).pack(expand=1, fill='both')
        center_frame = Frame(option_frame, background=self.colours.DataBackground)
        center_frame.pack(expand=0, fill='both')
        Frame(option_frame, background=self.colours.DataBackground).pack(expand=1, fill='both')

        return center_frame

    # ===================================================================================
    # standard page
    # ===================================================================================
    def create_standard_page(self, notebook_pages_info: Optional[list[NoteBookPageInfo]] = None):
        """Create the 'normal' page after the main page has fulfilled its purpose"""

        # if the page is already created, do not recreate it
        if self._standard_page_created:
            if self._top_level_notebook:
                self._top_level_notebook.select(self._default_notebook_page)
                self._top_level_notebook.event_generate("<<NotebookTabChanged>>")
                return

        # create the page
        self._standard_page_created = True
        mw = self.mw
        self._front_page_frame.destroy()

        # frame
        main_page_frame = Frame(mw, borderwidth=1, relief='ridge')
        main_page_frame.pack(side='top', expand=1, fill='both')

        self._notebook_pages_info = notebook_pages_info

        # Add notebooks if required
        if self._notebook_pages_info is not None:
            notebook = Notebook(main_page_frame)
            notebook.pack(expand=1, fill='both')
            self._top_level_notebook = notebook
            self.dict_of_frames = self._create_notebook_pages(notebook, self._notebook_pages_info)

    # ===================================================================================
    # create notebook pages
    # ===================================================================================
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
            frame = Frame(self.mw, **info.frame_args)
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
    #     """Reset the GUI_Pages when a new schedule is read."""
    #
    #     if self._standard_page_created:
    #         if self._top_level_notebook:
    #             self._top_level_notebook.select(self._default_notebook_page)
    #             self._top_level_notebook.event_generate("<<NotebookTabChanged>>")
    #     else:
    #         self.create_standard_page()

    # ===================================================================================
    # waiting routines
    # ===================================================================================
    def wait_for_it(self, title, msg):
        self.stop_waiting()

        self._wait = self.mw.winfo_toplevel()
        self._wait.title = title
        Label(self._wait, text=msg).pack(expand=1, fill='both')

        self._wait.geometry('300x450')
        self.mw.update()

    def stop_waiting(self):
        if self._wait:
            self._wait.destroy()
        self._wait = None

    def _exit_schedule(self, *_):
        self.mw.destroy()

    # ========================================================================
    # choose file
    # ========================================================================
    def select_file_to_save(self) -> str:
        return self._select_file(partial(fd.asksaveasfilename,
                                         defaultextension="csv", title="Save File As"))

    def select_file_to_open(self) -> str:
        return self._select_file(partial(fd.askopenfilename,
                                         title='Open a file for ' + str(self._preferences.semester())))

    def _select_file(self, select_gui) -> str:
        current_dir = self._preferences.current_dir() or self._preferences.home_directory()
        kwargs = {"filetypes": (
            ('schedule files', '*.csv'),
            ('All files', '*.*')
        )}

        if current_dir is not None:
            kwargs["initialdir"] = current_dir

        filename = select_gui(**kwargs)
        return filename

    # ========================================================================
    # message boxes
    # ========================================================================
    def show_error(self, title: str, msg: str, detail: str = ""):
        showerror(title=title, message=msg, detail=detail, icon='error')

    def show_message(self, title: str, msg: str, detail: str = ""):
        showinfo(title=title, message=msg, detail=detail, icon='info')

    def ask_yes_no(self, title: str, msg: str, detail: str = ""):
        return askyesnocancel(title=title, message=msg, detail=detail, icon='info')