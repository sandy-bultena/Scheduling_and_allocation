from __future__ import annotations
from typing import Callable


class NoteBookPageInfo:
    def __init__(self, name: str,
                 tab_changed_handler: callable = lambda *_: {},
                 subpages: list[NoteBookPageInfo] = None,
                 frame_args: dict = None,
                 # creation_handler: Callable[[str], None] = lambda name: print(f"Creating {name}"),
                 is_default_page: bool = False):
        """
        Create a NoteBookPageInfo instance

        :param name: Name of the _notebook tab
        :param tab_changed_handler: Method called when the tab is selected
        :param subpages: Sub-tabs that should be included
        :param frame_args:  Any arguments that should be passed to the Frame constructor on creation (tkinter.Frame NOT tkinter.ttk.Frame)
        :creation_handler:  A method to be called once the frame is created, to instantiate any sub-elements. Passes in the Frame object
        """
        self.name = name
        self.tab_selected_handler = self.tab_selected_handler = tab_changed_handler
        self.subpages = subpages if subpages is not None else []
        self.id = -1
        self.frame_args = frame_args if frame_args is not None else {}
        # self.creation_handler = creation_handler
        self.is_default_page = is_default_page
