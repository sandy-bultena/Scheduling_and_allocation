from ..Export import DrawView
from ..GUI.ViewTk import ViewTk
from ..Schedule.Block import Block
from ..Schedule.Lab import Lab
from ..Schedule.Schedule import Schedule
from ..Schedule.Stream import Stream
from ..Schedule.Teacher import Teacher


class View:
    """View - describes the visual representation of a Schedule."""

    # =================================================================
    # global and package variables
    # =================================================================
    undo_number = ""
    redo_number = ""
    clicked_block = 0
    days = DrawView.days
    times = DrawView.times
    earliest_time = min(times.keys())
    latest_time = max(times.keys())
    max_id = 0

    # =================================================================
    # getters/setters
    # =================================================================
    # TODO: Decide which of these to keep, beyond id and gui_blocks.
    @property
    def schedule(self) -> Schedule:
        """Get/Set the schedule object."""
        return self._schedule

    @schedule.setter
    def schedule(self, value: Schedule):
        self._schedule = value

    @property
    def gui(self) -> ViewTk:
        """Returns the GUI object for this view."""
        return self._gui

    @gui.setter
    def gui(self, value: ViewTk):
        self._gui = value

    @property
    def id(self) -> int:
        """Returns the unique ID for this View object."""
        return self._id

    @property
    def schedulable(self) -> Teacher | Lab | Stream:
        """Gets/Sets the Teacher, Lab, or Stream associated to this View."""
        return self._obj

    @schedulable.setter
    def schedulable(self, value: Teacher | Lab | Stream):
        self._obj = value

    @property
    def type(self):
        """Gets/Sets the type of this View object."""
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def blocks(self) -> list[Block]:
        """Gets/Sets the Blocks of this View object. An array."""
        return self._blocks

    @blocks.setter
    def blocks(self, value: list[Block]):
        self._blocks = value

    @property
    def gui_blocks(self):
        """Gets the GuiBlocks of this View object."""
        return self._gui_blocks

    @property
    def views_manager(self):
        """Gets/Sets the ViewsManager of this View object."""
        return self._views_manager

    @views_manager.setter
    def views_manager(self, value):
        self._views_manager = value

