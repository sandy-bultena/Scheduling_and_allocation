"""
# ============================================================================
# MAIN PAGE - Gui entry point to the application(s)
#
# - Forms base class for Scheduler and Allocation applications
#
# EVENT HANDLERS - None
# ============================================================================

"""
from __future__ import annotations

import platform
from functools import partial

from tkinter.ttk import Notebook
from tkinter import *
from tkinter import filedialog as fd
from typing import Optional, TYPE_CHECKING, Callable

from tkinter.messagebox import showerror, showinfo, askyesnocancel

from schedule.Tk import FindImages
from schedule.Tk import set_default_fonts_and_colours, TkColours, TkFonts
from schedule.Tk import generate_menu, make_toolbar
from schedule.gui_pages.note_book_frame_tk import NoteBookFrameTk, TabInfoProtocol
from schedule.Tk import MenuItem, ToolbarItem
from schedule.Utilities.Preferences import Preferences

if TYPE_CHECKING:
    pass

Operating_system = platform.system().lower()

MAIN_FRAME_HEIGHT = 400
MAIN_FRAME_WIDTH = 800
WELCOME_WIDTH = 600
WELCOME_HEIGHT = 600


class MainPageBaseTk:
    """Generic main page for Scheduler and Allocation Manager apps"""
    bin_dir = None

    # ===================================================================================
    # constructor
    # ===================================================================================
    def __init__(self, title, preferences: Preferences):
        """
        main page
        :param title:
        :param preferences: a preference object (color scheme, last opened file, etc)
        """

        # public properties
        self.dark_mode = False
        self.colours: Optional[TkColours] = None
        self.fonts: Optional[TkFonts] = None
        self.dict_of_frames: dict[str, Frame] = dict()
        self.logo: Optional[PhotoImage] = None
        self.mw: Optional[Tk] = None
        self.notebook_tab_changed_handler: Callable[[str,Frame], None] = lambda a,b: None

        # private properties
        self._preferences = preferences
        self._notebook_frame: Optional[NoteBookFrameTk] = None
        self._wait = None
        self.notebook_tabs_info: list[TabInfoProtocol] | None = None
        self._front_page_frame: Optional[Frame] = None
        self._toolbar = None
        self._default_notebook_page: int = 0
        self._top_level_notebook: Optional[Notebook] = None

        # Create the Tk main window
        self.mw = self._create_toplevel(title)

        # colors and fonts
        self.colours, self.fonts = set_default_fonts_and_colours(self.mw, invert=self.dark_mode)

        # set the filename so that it can be bound later
        self._status_bar_file_info: StringVar = StringVar(value="None")

        # set the dirty text so it can be bound later
        self._status_bar_dirty: StringVar = StringVar(value="")

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
        """
        Using the info, create menu and toolbar for this app
        :param buttons: a list of buttons for the toolbar
        :param toolbar_info: information about buttons/callbacks for the toolbar
        :param menu_details: all the details required for the menu
        """

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
    # welcome page
    # ===================================================================================
    def create_welcome_page_base(self, logo: PhotoImage | None = None) -> Frame:
        """
        Creates the very first page that is shown to the user
        :param logo: image to use as part of the front page header
        :return: the frame for the super class to use to add whatever they want
        """
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
        # frame for holding buttons for starting the scheduling/allocation tasks
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
    # standard page with notebook
    # ===================================================================================
    def create_standard_page(self, notebook_pages_info: Optional[list[TabInfoProtocol]] = None, reset=False):
        """
        Create the 'normal' page after the main page has fulfilled its purpose
        :param notebook_pages_info: which tabs, and callbacks, etc are in the notebook being created
        :param reset: should the notebook be re-drawns
        """

        # if the page is already created, do not recreate it
        if self._notebook_frame is not None or reset:
            if self._notebook_frame.main_notebook_frame:
                self._notebook_frame.main_notebook_frame.select(self._default_notebook_page)
                self._notebook_frame.main_notebook_frame.event_generate("<<NotebookTabChanged>>")
                return

        # create the page
        mw = self.mw
        self._front_page_frame.destroy()

        # frame
        main_page_frame = Frame(mw, borderwidth=1, relief='ridge')
        main_page_frame.pack(side='top', expand=1, fill='both')
        self._notebook_frame = NoteBookFrameTk(self.mw.winfo_toplevel(), main_page_frame, notebook_pages_info,
                                               self.notebook_tab_changed_handler)


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

    # ===================================================================================
    # create top level
    # ===================================================================================
    def _create_toplevel(self, title):
        """Create the top level window, specify fonts and colors"""
        # create main window and frames
        mw = Tk()
        mw.title(title)
        mw.geometry(f"{WELCOME_HEIGHT}x{WELCOME_WIDTH}")

        # when clicking the 'x' in the corner of the window, call _exit_schedule
        mw.protocol("WM_DELETE_WINDOW", self._exit_schedule)

        # have main window pop-up and have focus
        # https://stackoverflow.com/questions/8691655/how-to-put-a-tkinter-window-on-top-of-the-others/8691795
        mw.lift()
        mw.call('wm', 'attributes', '.', '-topmost', True)
        mw.after_idle(self.mw.call, 'wm', 'attributes', '.', '-topmost', False)
        mw.focus_force()

        return mw

    # ===================================================================================
    # start event loop
    # ===================================================================================
    def start_event_loop(self):
        """time_start the Tk event main event loop"""
        self.mw.mainloop()

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
