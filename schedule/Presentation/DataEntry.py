from collections import deque
from time import sleep

import schedule.Schedule.Lab
import schedule.Schedule.Stream
import schedule.Schedule.Teacher

'''
=head1 NAME
DataEntry - provides methods/objects for entering teachers/labs/etc data
=head1 VERSION
Version 6.00
=head1 SYNOPSIS
    use Schedule::Schedule;
    use Presentation::ViewsManager;
    use GUI::DataEntryTk;

    my $Dirtyflag   = 0;
    my $mw          = MainWindow->new();
    my $Schedule = Schedule->read_YAML('myschedule_file.yaml');
    my $views_manager = ViewsManager->new( $mw, \$Dirtyflag, \$Schedule );

    # create a data entry list
    # NOTE: requires $views_manager just so that it can update
    #       the views if data has changed (via the dirty flag)

    my $de = DataEntry->new( $mw, $Schedule->teachers,
                    $Schedule, \$Dirtyflag, $views_manager );
=head1 DESCRIPTION
A generic data entry widget

'''


class DataEntry:
    # =================================================================
    # Class Variables
    # =================================================================
    max_id = 0
    Delete_queue = deque()
    room_index = 1
    id_index = 0

    # =================================================================
    # Properties
    # =================================================================
    @property
    def gui(self):
        """Gets or sets the DataEntryTK object"""
        return self._gui

    @gui.setter
    def gui(self, val):
        self._gui = val

    @property
    def schedule(self):
        """Gets or sets the Schedule object."""
        return self._schedule

    @schedule.setter
    def schedule(self, sched):
        self._schedule = sched

    @property
    def dirty(self):
        """Gets or sets the dirty_flag pointer (whether the schedule has changed since the
        last save)."""
        return self._dirty_ptr()

    @dirty.setter
    def dirty(self, is_dirty):
        self._dirty_ptr(is_dirty)

    def _dirty_ptr(self, is_dirty: bool = None):
        if is_dirty is not None:
            self.__dirty_ptr = is_dirty
        return self.__dirty_ptr

    @property
    def type(self) -> str:
        """Gets the Schedulable type (Teacher/Lab/Stream)."""
        return self.schedule.get_schedulable_object_type(self.schedulable_list_obj)

    @property
    def schedulable_class(self):
        """Gets the Scheduable class name (Teacher / Lab / Stream)"""
        return self.type.title()

    @property
    def schedulable_list_obj(self):
        """Gets or sets the object containing the list of schedulable objects."""
        return self._list_obj

    @schedulable_list_obj.setter
    def schedulable_list_obj(self, new_obj):
        self._list_obj = new_obj

    @property
    def col_titles(self):
        """Gets or sets the titles for each individual column."""
        return self._col_titles

    @col_titles.setter
    def col_titles(self, titles: list[str]):
        self._col_titles = titles

    @property
    def col_widths(self):
        """Gets or sets the widths required for each individual column."""
        return self._col_widths

    @col_widths.setter
    def col_widths(self, widths: list[int]):
        self._col_widths = widths

    # =================================================================
    # new
    # =================================================================
    def __init__(self, frame, schedulable_list_obj, schedule, dirty_ptr, views_manager):
        """
        Creates the basic DataEntry (a simple matrix).

        - Parameter frame: the Tk frame where this object's Entry widgets will be drawn.
        - Parameter schedulable_list_obj: The type of schedulable object this Entry will handle
        (Teacher | Lab | Stream).
        - Parameter schedule: the Schedule object.
        - Parameter dirty_ptr: a reference to the dirty pointer.
        - Parameter views_manager: the object which manages the views.
        """
        DataEntry.Delete_queue = []

        self._dirty_ptr(dirty_ptr)
        self.schedulable_list_obj = schedulable_list_obj
        self.schedule = schedule

        # ---------------------------------------------------------------
        # get objects to process?
        # ---------------------------------------------------------------
        objs = schedulable_list_obj.list()
        rows = len(objs)

        # ---------------------------------------------------------------
        # what are the columns?
        # ---------------------------------------------------------------
        methods = []
        titles = []
        disabled = []
        widths = []
        sort_by = ''
        delete_sub = None  # TODO: Come back to these two. They seem to be unfinished or unused.
        de = None

        if self.type.lower() is 'teacher':
            methods.extend(["id", "firstname", "lastname", "release"])
            titles.extend(['id', 'first name', 'last name', 'RT'])
            widths.extend([4, 20, 20, 8])
            sort_by = 'lastname'

        elif self.type.lower() is 'lab':
            methods.extend(["id", "number", "descr"])
            titles.extend(['id', 'room', 'description'])
            widths.extend([4, 7, 40])
            sort_by = 'number'

        elif self.type.lower() is 'stream':
            methods.extend(["id", "number", "descr"])
            titles.extend(['id', 'number', 'description'])
            widths.extend([4, 10, 40])
            sort_by = 'number'

        self._col_sortby = sort_by
        self._col_methods = methods
        self.col_titles = titles
        self.col_widths = widths

        # ---------------------------------------------------------------
        # create the table entry object
        # ---------------------------------------------------------------
        gui = DataEntryTk(self, frame, _cb_delete_obj, _cb_save)
        self.gui = gui

        row = self.refresh()

    # =================================================================
    # refresh the tables
    # =================================================================
    def refresh(self, list_obj=None):
        if list_obj: self.schedulable_list_obj = list_obj

        objs: list = self.schedulable_list_obj.list()
        sort_by = self._col_sortby

        # Create a 2-d array of the data that needs to be displayed.
        data = []
        for obj in sorted(objs, key=lambda x: x.sort_by):
            row = []
            for method in self._col_methods:
                row.append(obj.method)
            data.append(row)

        # refresh the GUI
        self.gui.refresh(data)

        DataEntry.Delete_queue = []

    # =================================================================
    # Save updated data
    # =================================================================
    currently_saving = 0  # Static counter which keeps track of how many files are currently being

    # saved.

    # region CALLBACKS (EVENT HANDLERS)
    def _cb_save(self):
        """Save any changes that the user entered in the GUI form."""
        schedule = self.schedule
        dirty_flag = 0

        # Get data from the GUI object.
        all_data = self.gui.get_all_data()

        # Just in case saving is already in progress, wait before continuing.
        if DataEntry.currently_saving > 2:
            return  # 2 is too many.
        if DataEntry.currently_saving:
            sleep(1)
        DataEntry.currently_saving += 1

        # Read data from the data object.
        for row in all_data:
            data = row.copy()

            # If this is an empty row, do nothing.
            if data is None:
                continue  # Not the right if-statement. Come back to this.

            # --------------------------------------------------------------------
            # if this row has an ID, then we need to update the
            # corresponding object
            # --------------------------------------------------------------------
            if data[DataEntry.id_index] and data[DataEntry.id_index] != '':
                schedulable_list_obj = self._list_obj
                o = schedulable_list_obj.get(data[DataEntry.id_index])

                # Loop over each method used to get info about this object.
                col = 1
                for method in self._col_methods:
                    # Set dirty flag if new data is not the same as the currently set property.
                    dirty_flag += 1 if o.method != data[col - 1] else 0

                    # Set the property to the data. TODO: Verify that this works.
                    eval(f"{o}.{method} = {data[col - 1]}")

            # --------------------------------------------------------------------
            # if this row does not have an ID, then we need to create
            # corresponding object
            # --------------------------------------------------------------------
            else:
                schedulable_list_obj = self._list_obj

                # Create parameters to pass to the new object.
                parms = {}
                col = 1
                for method in self._col_methods:
                    parms[method] = data[col - 1]
                    col += 1

                # Create the new Object and add it to the list.
                new_obj = eval(f"{self.schedulable_class}({parms})")
                eval(f"{self.schedulable_list_obj.add(new_obj)}")

                dirty_flag += 1
        # ------------------------------------------------------------------------
        # go through delete queue and apply changes
        # ------------------------------------------------------------------------
        while len(DataEntry.Delete_queue) > 0:
            schedulable_list_obj = DataEntry.Delete_queue.popleft()
            o = DataEntry.Delete_queue.popleft()

            if o:
                dirty_flag += 1
                if isinstance(o, schedule.Schedule.Teacher.Teacher):
                    schedule.remove_teacher(o)
                elif isinstance(o, schedule.Schedule.Stream.Stream):
                    schedule.remove_stream(o)
                elif isinstance(o, schedule.Schedule.Lab.Lab):
                    schedule.remove_lab(o)

        # if there have been changes, set global dirty flag and do what is necessary.
        if dirty_flag > 0:
            self.set_dirty()
        DataEntry.currently_saving = 0
        # endregion
