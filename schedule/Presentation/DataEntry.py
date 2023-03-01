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
    Delete_queue = []
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
        for obj in sorted(objs, key=sort_by):
            row = []
            for method in self._col_methods:
                row.append(obj.method)
            data.append(row)

        # refresh the GUI
        self.gui.refresh(data)

