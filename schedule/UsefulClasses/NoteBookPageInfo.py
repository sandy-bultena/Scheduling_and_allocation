from __future__ import annotations
from tkinter import Frame


class NoteBookPageInfo:
    def __init__(self, name: str, event_handler: callable = lambda *_: {}, subpages: list[NoteBookPageInfo] = [],
                 frame_args: dict = None, frame_callback=None, frame_type=Frame):
        """
        Create a NoteBookPageInfo instance.

        ----
        Parameters:
        - name > Name of the notebook tab
        - event_handler > Method called when the tab is selected
        - subpages > Sub-tabs that should be included
        - frame_args > Any arguments that should be passed to the Frame constructor on creation (tkinter.Frame NOT tkinter.ttk.Frame)
        - frame_callback > A method to be called once the frame is created, to instantiate any sub-elements. Passes in the Frame object
        """
        self.name = name
        self.handler = self.event_handler = event_handler
        self.subpages = subpages
        self.id = -1
        self.panel: frame_type | None = None
        self.frame_type = frame_type
        self.frame_args = frame_args if frame_args is not None else {}
        self.frame_callback = frame_callback
