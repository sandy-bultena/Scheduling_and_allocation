from functools import partial
from tkinter import *


class ViewsManagerTk:
    def __init__(self, gui):
        self._main_gui = gui
        self.main_window = gui.mw
        self._button_refs: dict[str, Button] = {}

    @property
    def main_window(self):
        """Gets the MainWindow object."""
        return self._main_window

    @main_window.setter
    def main_window(self, value):
        self._main_window = value

    def add_button_refs(self, btn: Button, obj):
        """Adds a button reference to the dictionary of all button references and the Object it is associated to.

        Parameters:
            btn: A button object.
            obj: A schedulable object (Teacher/Lab/Stream)"""
        # Save
        self._button_refs[obj] = btn
        return self

    def __button_refs(self) -> dict[str, Button]:
        """Returns a dict of all button dicts."""
        return self._button_refs

    def reset_button_refs(self):
        """Resets the dictionary of button references."""
        self._button_refs.clear()

    def set_button_colour(self, obj, view_conflict):
        """Sets the colour of the button which is used to create the view.

        The colour is dependent on the conflict for this particular view."""
        # Get the button associated with the current teacher/lab/stream.

        button_pts = self._button_refs
        btn = button_pts[obj]

        # Set button colour to conflict colour if there is a conflict.
        # TODO: Come back to this once FontsAndColoursTk has been implemented.

    def create_buttons_for_frame(self, frame: Frame, schedulables_by_type, command_func):
        """Populates frame with buttons for all Teachers, Labs, or Streams depending on type,
        in alphabetical order.

        Parameters:
            frame: Frame object which will be drawn on.
            schedulables_by_type: An object that defines everything needed to know what schedulable objects are available.
            command_func: Callback function to create a view if the button is clicked."""
        schedulables = schedulables_by_type.named_schedulable_objs
        type = schedulables_by_type.type

        row = 0
        col = 0

        # determine how many buttons should be on one row.
        arr_size = len(schedulables)
        divisor = 2
        if arr_size > 10:
            divisor = 4

        # For every view choice object...
        for named_schedulable_obj in schedulables:
            name = named_schedulable_obj.name

            # Create the command array reference including the ViewManager, the Teacher/Lab/Stream,
            # and its type.
            command = [command_func, self, name, type]

            # Create the button on the frame.
            btn = Button(frame, text=name, command=partial(
                command_func, self, name, type
            ))
            btn.grid(row=row, column=col, sticky="nsew",
                     ipadx=30, ipady=10)

            # Pass the button reference to the event handler # NOTE: ?
            # TODO: Figure this out. Not even sure that this is necessary.
            command.append(btn)

            # add it to the dict of button references.
            self.add_button_refs(btn, named_schedulable_obj)

            col += 1

            # Reset to next row.
            if col >= (arr_size / divisor):
                row += 1
                col = 0
