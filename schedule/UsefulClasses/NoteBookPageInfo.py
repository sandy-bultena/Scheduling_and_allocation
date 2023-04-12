from __future__ import annotations
from tkinter import Frame

class NoteBookPageInfo:
    def __init__(self, name : str, event_handler, subpages : list[NoteBookPageInfo], panel = None):
        self.name = name
        self.handler = self.event_handler = event_handler
        self.subpages = subpages
        self.id = -1
        self.panel = panel if panel else Frame()