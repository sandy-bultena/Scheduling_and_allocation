from dataclasses import dataclass, field
from functools import partial
from tkinter.ttk import Notebook
from tkinter import *
from typing import Optional, Callable, Protocol, Any


@dataclass
class TabInfoProtocol(Protocol):
        name: str
        label: str
        subpages: list = field(default_factory=list)
        frame_args: dict[str, Any] =  field(default_factory=dict)
        creation_handler: Callable = lambda *_: None
        is_default_page: bool = False


def _expose_widgets(widget):
    """weird shit happens on MAC in that widgets are not shown in tab... this forces them to be shown"""
    widget.event_generate("<Expose>")
    for child in widget.winfo_children():
        _expose_widgets(child)


class NoteBookFrameTk:
    """creates notebook, recursively, until all notebook tabs are created"""
    # ===================================================================================
    # constructor
    # ===================================================================================
    def __init__(self, mw: Toplevel, main_page_frame: Frame,
                 tabs_info: Optional[list[TabInfoProtocol]] = None,
                 tab_changed_handler: Callable[[str, Frame], None] = lambda *_: None):

        self._default_notebook_page = None
        self.tabs_info = tabs_info
        self.mw = mw
        self.frame = main_page_frame
        self.tab_frames: dict[tuple[Notebook,int], tuple[str,Frame]] = {}
        self.tab_changed_handler = tab_changed_handler
        self.main_notebook_frame = None

        self.recursive_notebook_creation(self.frame, tabs_info)


    # ===================================================================================
    # create notebook pages
    # ===================================================================================
    def recursive_notebook_creation(self, notebook_frame: Frame, tabs_info: list[TabInfoProtocol]):

        if tabs_info is None:
            return

        # Create notebook if required
        notebook = Notebook(notebook_frame)
        notebook.pack(expand=1, fill='both')

        if self.main_notebook_frame is None:
            self.main_notebook_frame = notebook

        for info in tabs_info:
            # create a frame and add to the notebook
            frame = Frame(self.mw, **info.frame_args)
            notebook.add(frame, text=info.label)
            notebook_index = notebook.index(frame)

            # save the frame and name for this tab index
            self.tab_frames[(notebook,notebook_index)] = (info.name, frame)

            # set the page that should be shown by default
            if info.is_default_page:
                self._default_notebook_page = notebook_index

            # if this notebook page has sub-pages, then set them up as well
            if info.subpages:
                self.recursive_notebook_creation(frame, info.subpages)

            # call the 'create handler' for this page
            if info.creation_handler:
                info.creation_handler(info.name, frame)

        # add the binding for changing of events, and include a list of events for each tab change
        notebook.bind("<<NotebookTabChanged>>", partial(self._tab_changed, notebook))

    def _tab_changed(self, notebook: Notebook, *_):
        """calls the tab changed callback when the tab has changed"""
        index = notebook.index(notebook.select())
        tab_name, frame  = self.tab_frames.get((notebook,index), None)
        _expose_widgets(frame)
        self.tab_changed_handler(tab_name, frame)


    # def update_for_new_schedule_and_show_page(self):
    #     """Reset the GUI_Pages when a new schedule is read."""
    #
    #     if self._notebook_frame:
    #         if self._top_level_notebook:
    #             self._top_level_notebook.select(self._default_notebook_page)
    #             self._top_level_notebook.event_generate("<<NotebookTabChanged>>")
    #     else:
    #         self.create_standard_page()
