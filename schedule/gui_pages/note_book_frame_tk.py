from functools import partial
from tkinter.ttk import Notebook
from tkinter import *
from typing import Optional, Callable

from schedule.Utilities import NoteBookPageInfo


def _expose_widgets(widget):
    widget.event_generate("<Expose>")
    for child in widget.winfo_children():
        _expose_widgets(child)


def _tab_changed(notebook: Notebook, event_handlers: dict, pages: dict[str, Frame], *_):
    """calls the appropriate callback when the tab has changed"""
    index = notebook.index(notebook.select())
    f = event_handlers.get(index, lambda *_: {})
    f()


class NoteBookFrameTk:
    # ===================================================================================
    # constructor
    # ===================================================================================
    def __init__(self, mw: Toplevel, main_page_frame: Frame,
                 notebook_pages_info: Optional[list[NoteBookPageInfo]] = None):
        self.notebook_pages_info = notebook_pages_info
        self.mw = mw

        # Add notebooks if required
        if self.notebook_pages_info is not None:
            notebook = Notebook(main_page_frame)
            notebook.pack(expand=1, fill='both')
            self.top_level_notebook = notebook
            self.dict_of_frames = self._create_notebook_pages(notebook, self.notebook_pages_info)

    # ===================================================================================
    # create notebook pages
    # ===================================================================================
    def _create_notebook_pages(self, notebook: Notebook, pages_info: list[NoteBookPageInfo]):
        """
        create Notebook with specified pages described by pages_info
        :param notebook: Notebook object
        :param pages_info: information about how we want the page to look
        :return: a dictionary of frames contained within each Notebook tab

        """
        tab_selected_handlers: dict[int, Callable] = dict()
        pages: dict[str, Frame] = dict()

        for info in pages_info:
            # create a frame and add to the notebook
            frame = Frame(self.mw, **info.frame_args)
            notebook.add(frame, text=info.name)
            notebook_index = notebook.index(frame)

            # set up the event handlers
            tab_selected_handlers[notebook_index] = info.tab_selected_handler \
                if info.tab_selected_handler else lambda *_: {}

            # save the notebook frame in dictionary by page name
            pages[info.name.lower()] = frame

            # set the page that should be shown by default
            if info.is_default_page:
                self._default_notebook_page = notebook_index

            # if this notebook page, has sub-pages, then set them up as well
            if info.subpages:
                sub_page_frame = Notebook(frame)
                sub_page_frame.pack(expand=1, fill='both')
                sub_pages = self._create_notebook_pages(sub_page_frame, info.subpages)
                pages.update(sub_pages)

            # call the 'create handler' for this page
            if info.creation_handler:
                info.creation_handler(info.name.lower())

        # add the binding for changing of events, and include a list of events for each tab change
        notebook.bind("<<NotebookTabChanged>>", partial(_tab_changed, notebook, tab_selected_handlers, pages))

        return pages

    # def update_for_new_schedule_and_show_page(self):
    #     """Reset the GUI_Pages when a new schedule is read."""
    #
    #     if self._notebook_frame:
    #         if self._top_level_notebook:
    #             self._top_level_notebook.select(self._default_notebook_page)
    #             self._top_level_notebook.event_generate("<<NotebookTabChanged>>")
    #     else:
    #         self.create_standard_page()
