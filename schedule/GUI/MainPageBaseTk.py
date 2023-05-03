import sys
from os import path

import Pmw

sys.path.append(path.dirname(path.dirname(__file__)))

from tkinter.ttk import Notebook
from tkinter import Tk as root, Label, Menu, StringVar, PhotoImage, Frame, BooleanVar
from tkinter.messagebox import showerror, showinfo, askyesnocancel

from GUI.FontsAndColoursTk import FontsAndColoursTk
from Tk import FindImages
from Tk.ToolBar import ToolBar
from Presentation import globals
from GUI import dirty
from functools import partial
from PerlLib import Colour
from UsefulClasses.NoteBookPageInfo import NoteBookPageInfo

import re, platform
O = platform.system().lower()

MAIN_FRAME_HEIGHT = 400
MAIN_FRAME_WIDTH = 800
WELCOME_WIDTH = 600
WELCOME_HEIGHT = 600

class MainPageBaseTk:
    def start_event_loop(self):
        self.mw.mainloop()

    def bind_dirty_flag(self):
        """Watches the dirty_flag, and reacts accordingly when it changes"""
        dirty.init_dirty_flag()
        globals.init_dirty_flag(dirty.set_, dirty.unset, dirty.check)
        dirty.dirty_flag.trace_add('write', partial(
            lambda dft, *_: dft.set("NOT SAVED" if globals.is_data_dirty() else ""),
            self.dirty_flag_text))
    
    def define_exit_callback(self, exit = lambda *_: {}):
        """If defined, exit callback will be executed just prior to the call to 'exit'"""
        self.exit_callback = exit
    
    def create_main_window(self, title = 'Main Window'):
        # create main window and frames
        mw = self.mw = root()
        Pmw.initialise(mw)
        mw.title(title)
        self.frame = Frame(mw, height = MAIN_FRAME_HEIGHT).pack(side = 'left')
        mw.geometry(f"{WELCOME_HEIGHT}x{WELCOME_WIDTH}")

        self.dirty_flag_text = StringVar(value = "")
        self.pages = dict()

        # when clicking the 'x' in the corner of the window, call _exit_schedule
        mw.protocol("WM_DELETE_WINDOW", self._exit_schedule)

        # colours and fonts
        FontsAndColoursTk.setup(mw)
        self.fonts = FontsAndColoursTk.fonts
        self.colours = FontsAndColoursTk.colours
    
    def create_menu_and_toolbars(self, buttons : list[str], actions : dict[str, dict[str, ]], menu_details : list[dict]):
        def _generate_menu(menu_details :list[dict], parent : Menu):
            for o in menu_details:
                menubar = Menu(parent, tearoff = o.get('tearoff', 0))
                if o.get('menuitems', [{}])[0].get('menuitems', None):  # if the first element in menuitems has it's own sub-elements, recurse
                    _generate_menu(o.get('menuitems', []), menubar)
                else:                                                   # otherwise, create the elements
                    for i in o.get('menuitems', []):
                        if i == 'separator': menubar.add_separator()
                        else: menubar.add(**i)
                parent.add(itemType = o.get('itemType', 'command'), label = o.get('label', 'Menu Item'), menu = menubar)

        mw = self.mw
        image_dir = FindImages.get_image_dir()

        # create menu
        menu = Menu(mw)
        _generate_menu(menu_details, menu)

        mw.configure(menu = menu)

        # create toolbar
            # colours may need to be moved to separate .config calls
        toolbar = self.toolbar = ToolBar(mw, buttonbg=self.colours['WorkspaceColour'], hoverbg=self.colours['ActiveBackground'])

        # create all the buttons
        for button in buttons:
            # if button not defined, insert a divider
            if not button:
                toolbar.bar()
                continue

            # add button
            toolbar.add(
                name = button,
                image = path.join(image_dir, actions.get(button, {}).get('image', f'{button}.gif')),
                command = actions.get(button, {}).get('code'),
                hint = actions.get(button, {}).get('hint'),
                shortcut = actions.get(button, {}).get('sc')
            )
        
        # pack the toolbar
        toolbar.pack(side = 'top', expand = 0, fill = 'x')

        # bind all the accelerators
        mw.bind('<Control-Key-o>', actions.get('open', {}).get('code'))
        mw.bind('<Control-Key-s>', actions.get('save', {}).get('code'))
        mw.bind('<Control-Key-n>', actions.get('new', {}).get('code'))
        mw.bind('<Control-Key-e>', self._exit_schedule)

        # if darwin, also bind the 'command' key for MAC users
        if re.search('darwin', O):
            mw.bind('<Meta-Key-o>', actions.get('open', {}).get('code'))
            mw.bind('<Meta-Key-s>', actions.get('save', {}).get('code'))
            mw.bind('<Meta-Key-n>', actions.get('new', {}).get('code'))
            mw.bind('<Meta-Key-e>', self._exit_schedule)
    
    def create_status_bar(self, current_filename : StringVar = None):
        """Create a status bar for current filename and dirty flag"""
        mw = self.mw
        if not current_filename: current_filename = StringVar()
        # choose what colour to show dirty flag text based on WorkspaceColour
        red = "#880000" if Colour.is_light(self.colours['WorkspaceColour']) else '#ff0000'

        # draw frame and labels for current filename and dirty flag
        (status_frame := Frame(mw, borderwidth = 0, relief = 'flat'))\
            .pack(side = 'bottom', expand = 0, fill = 'x')
        
        Label(status_frame, textvariable = current_filename, borderwidth = 1, relief = 'ridge')\
            .pack(side = 'left', expand = 1, fill = 'x')
        
        Label(status_frame, textvariable = self.dirty_flag_text, borderwidth = 1, relief = 'ridge', width = 15, foreground = red)\
            .pack(side = 'right', fill = 'x')
    
    def create_front_page(self, logo):
        """Creates the very first page that is shown to the user"""
        mw = self.mw
        self.front_page_frame = Frame(mw, borderwidth = 10, relief = 'flat', background = self.colours['DataBackground'])
        self.front_page_frame.pack(side = 'top', expand = 1, fill = 'both')
        if not logo: logo = FindImages.get_logo()

        # --------------------------------------------------------------
        # logo
        # --------------------------------------------------------------

        # create an image object of the logo
            # stored in self because tkinter doesn't keep references persistent
                # (ie they get garbage collected at method finish)
        self.logo = PhotoImage(file = logo)
        
        # frame and label
        Label(self.front_page_frame, image = self.logo, borderwidth = 5, relief = 'flat')\
            .pack(side = 'left', expand = 0)

        # --------------------------------------------------------------
        # frame for holding buttons for starting the scheduling tasks
        # --------------------------------------------------------------
        (option_frame := Frame(self.front_page_frame, bg = self.colours['DataBackground'], borderwidth = 10, relief = 'flat'))\
            .pack(side = 'left', expand = 1, fill = 'both')
        
        Frame(option_frame, bg = self.colours['DataBackground']).pack(expand = 1, fill = 'both')
        (center_frame := Frame(option_frame, bg = self.colours['DataBackground']))\
            .pack(expand = 0, fill = 'both')
        Frame(option_frame, bg = self.colours['DataBackground']).pack(expand = 1, fill = 'both')

        return center_frame
    
    def _create_standard_page(self):
        """Create the 'normal' page after the main page has fulfilled its purpose"""
        def tab_changed(notebook : Notebook, cmds : dict, *_):
            index = notebook.index(notebook.select())
            # if not set, default to empty lambda. if set and not None, call
            if (f := cmds.get(index, lambda *_: {})) is not None: f()
        
        def create_notebook(parent : Notebook, events : dict, pages : dict[int, Frame], tabs : list[NoteBookPageInfo], id_prefix : str = "", ):
            for info in tabs:
                info.panel = Frame(self.mw, **info.frame_args)
                parent.add(info.panel, text = info.name)
                i = parent.index(info.panel)
                events[i] = info.handler
                pages[id_prefix + str(i)] = info.panel
                info.id = id_prefix + str(i)

                if info.subpages:
                    sub_page_frame = Notebook(info.panel)
                    sub_page_frame.pack(expand = 1, fill = 'both')
                    sub_events = dict()
                    create_notebook(sub_page_frame, sub_events, pages, info.subpages, f"{i}-")

                if info.frame_callback: info.frame_callback(info.panel)
            parent.bind("<<NotebookTabChanged>>", partial(tab_changed, parent, events))
        
        mw = self.mw
        # my @caller = caller()

        # frame and label
        (main_page_frame := Frame(mw, borderwidth = 1, relief = 'ridge'))\
            .pack(side = 'top', expand = 1, fill = 'both')
        
        # create notebook
        self.notebook = Notebook(main_page_frame)
        self.notebook.pack(expand = 1, fill = 'both')

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
    
    def define_notebook_tabs(self, notebook_tabs : list[NoteBookPageInfo]):
        self.required_notebook_tabs = notebook_tabs
    
    def get_notebook_page(self, page_id : int) -> NoteBookPageInfo:
        return self.pages[page_id]
    
    def update_for_new_schedule_and_show_page(self, default_page_id: int = 0):
        """Reset the GUI when a new schedule is read. default_page_id must be the integer ID of a TOP-LEVEL notebook tab"""
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
    
    def show_error(self, title, message): showerror(title, message)

    # does this need to be implemented?
    def choose_file(self, curr_dir, file_types):
        raise NotImplementedError()
    
    def show_info(self, title, message): showinfo(title, message)

    def question(self, title, message):
        return askyesnocancel(title, message)
    
    def wait_for_it(self, title, msg):
        self.stop_waiting()

        self.wait = self.mw.winfo_toplevel()
        self.wait.title = title
        Label(self.wait, text = msg).pack(expand = 1, fill = 'both')

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
        m.update_for_new_schedule_and_show_page(0)

    from tkinter import Button

    m = MainPageBaseTk()
    m.create_main_window('My App')

    # tried to keep similar to existing Perl structure, but note (for menu_details):
        # - the type & label need to be called "itemType" and "label"
        # - to underline access keys, add the "underline" argument to the given item
            # - an int that represents the index of the char to be underlined
            # - note that on Windows 10/11, "Underline Access Keys" (Win Settings) must be ON
              # to view the underline. This is not the case in Perl
    m.create_menu_and_toolbars(['new', 'open', 'CSVimport', 'save', 'Mark Dirty', 'Mark Clean'], {
        'new': {
            'hint': 'Create new Schedule File',
            'code': lambda *_: print('New button pressed'),
        },
        'open': {
            'hint': 'Open Schedule File',
            'code': lambda *_: print('Open button pressed'),
            'sc': 'o'
        },
        'CSVimport': {
            'code': lambda *_: print('CSVimport button pressed'),
            'hint': 'Import Schedule from CSV',
        },
        'save': {
            'hint': 'Save Schedule File',
            'code': lambda *_: print('Save button pressed'),
        },
        'Mark Dirty': {
            'code': globals.set_dirty_flag,
            'hint': 'Mark Dirty (Keybind: D)',
            'image': 'trash-icon48.png',
            "sc": "d"
        },
        'Mark Clean': {
            'code': globals.unset_dirty_flag,
            'hint': 'Mark Clean (Keybind: C)',
            'image': 'mag.gif',
            "sc": "c"
        }
    }, [
        {
            'itemType': 'cascade',
            'label': 'File',
            'tearoff': 0,
            'menuitems': [
                {
                    'itemType': 'command',
                    'label': 'New Fall',
                    'accelerator': 'Ctrl-n',
                    'command': lambda *_: print("'File/New Fall' Selected")
                },
                {
                    'itemType': 'command',
                    'label': 'New Winter',
                    'accelerator': 'Ctrl-n',
                    'command': lambda *_: print("'File/New Winter' Selected")
                },
                {
                    'itemType': 'command',
                    'label': 'Open Fall',
                    'accelerator': 'Ctrl-o',
                    'command': lambda *_: print("'File/Open Fall' Selected")
                },
                {
                    'itemType': 'command',
                    'label': 'Open Winter',
                    'accelerator': 'Ctrl-o',
                    'command': lambda *_: print("'File/Open Winter' Selected")
                },
                'separator',
                {
                    'itemType': 'command',
                    'label': 'Save',
                    'underline': 0,
                    'accelerator': 'Ctrl-s',
                    'command': lambda *_: print("'File/Save' Selected")
                },
                {
                    'itemType': 'command',
                    'label': 'Save As',
                    'command': lambda *_: print("'File/Save As' Selected")
                },
                'separator',
                {
                    'itemType': 'command',
                    'label': 'Exit',
                    'underline': 0,
                    'accelerator': 'Ctrl-e',
                    'command': lambda *_: print("'File/Exit' Selected")
                },
            ]
        }, {
            'itemType': 'cascade',
            'label': 'Print',
            'tearoff': 0,
            'menuitems': [
                {
                    'itemType': 'cascade',
                    'label': 'PDF',
                    'tearoff': 0,
                    'menuitems': [
                        {
                            'itemType': 'command',
                            'label': 'Teacher Schedules',
                            'command': lambda *_: print("'Print/Teacher Schedules' selected")
                        },
                        {
                            'itemType': 'command',
                            'label': 'Lab Schedules',
                            'command': lambda *_: print("'Print/Lab Schedules' selected")
                        },
                        {
                            'itemType': 'command',
                            'label': 'Stream Schedules',
                            'command': lambda *_: print("'Print/Stream Schedules' selected")
                        },
                        'separator',
                        {
                            'itemType': 'command',
                            'label': 'Text Output',
                            'command': lambda *_: print("'Print/Text Output' selected")
                        }
                    ]
                },
                {
                    'itemType': 'cascade',
                    'label': 'Latex',
                    'tearoff': 0,
                    'menuitems': [
                        {
                            'itemType': 'command',
                            'label': 'Teacher Schedules',
                            'command': lambda *_: print("'Latex/Teacher Schedules' selected")
                        },
                        {
                            'itemType': 'command',
                            'label': 'Lab Schedules',
                            'command': lambda *_: print("'Latex/Lab Schedules' selected")
                        },
                        {
                            'itemType': 'command',
                            'label': 'Stream Schedules',
                            'command': lambda *_: print("'Latex/Stream Schedules' selected")
                        },
                        'separator',
                        {
                            'itemType': 'command',
                            'label': 'Text Output',
                            'command': lambda *_: print("'Latex/Text Output' selected")
                        },
                    ]
                }, {
                    'itemType': 'cascade',
                    'label': 'CSV',
                    'tearoff': 0,
                    'menuitems': [
                        {
                            'itemType': 'command',
                            'label': 'Save schedule as CSV',
                            'command': lambda *_: print("'CSV/Save schedule as CSV' selected")
                        }
                    ]
                }
            ]
        }
    ])
    
    option_frame = m.create_front_page(FindImages.get_logo())
    # in practice this is in a child class inheriting MainPageBaseTk, after super().create_front_page
    Button(option_frame, text = "View Notebook tabs", command = switch_to_notebook)\
        .pack(side = 'top', fill = 'y', expand = 0)
    
    m.create_status_bar(file := StringVar())
    
    m.bind_dirty_flag()
    
    def view_streams(f):
        Button(f, text = "View Streams tab", command = partial(m.update_for_new_schedule_and_show_page, 5))\
            .pack(side = 'top', fill = 'y', expand = 0)
    
    # NOTE: The event_handler method is called on every first subpage, even if it's not visible, as it's selected by default
    m.define_notebook_tabs([
        	NoteBookPageInfo("Schedules", lambda *_: print("Schedules called"), [
                NoteBookPageInfo("Schedules-2", lambda *_: print("Schedules/Schedules-2 called"), []),
                NoteBookPageInfo("Overview-2", lambda *_: print("Schedules/Overview-2 called"), [
                    NoteBookPageInfo("Schedules-3", lambda *_: print("Schedules/Overview/Schedules-3 called"), []),
                    NoteBookPageInfo("Overview-3", lambda *_: print("Schedules/Overview/Overview-3 called"), []),
                    NoteBookPageInfo("Courses-3", lambda *_: print("Schedules/Overview/Courses-3 called"), []),
                    NoteBookPageInfo("Teachers-3", lambda *_: print("Schedules/Overview/Teachers-3 called"), []),
                    NoteBookPageInfo("Labs-3", lambda *_: print("Schedules/Overview/Labs-3 called"), []),
                    NoteBookPageInfo("Streams-3", lambda *_: print("Schedules/Overview/Streams-3 called"), []),
                ], frame_callback = view_streams),
                NoteBookPageInfo("Courses-2", lambda *_: print("Schedules/Courses-2 called"), []),
                NoteBookPageInfo("Teachers-2", lambda *_: print("Schedules/Teachers-2 called"), []),
                NoteBookPageInfo("Labs-2", lambda *_: print("Schedules/Labs-2 called"), []),
                NoteBookPageInfo("Streams-2", lambda *_: print("Schedules/Streams-2 called"), []),
            ], frame_callback = view_streams),
            NoteBookPageInfo("Overview", lambda *_: print("Overview called"), [], frame_callback = view_streams),
            NoteBookPageInfo("Courses", lambda *_: print("Courses called"), [], frame_args = { 'background': 'purple' }, frame_callback = view_streams),
            NoteBookPageInfo("Teachers", lambda *_: print("Teachers called"), [], frame_callback = view_streams),
            NoteBookPageInfo("Labs", lambda *_: print("Labs called"), [], frame_callback = view_streams),
            NoteBookPageInfo("Streams", lambda *_: print("Streams called"), [], frame_callback = view_streams)
    ])

    m.define_exit_callback(lambda *_: print("Application exited"))
    
    m.start_event_loop()