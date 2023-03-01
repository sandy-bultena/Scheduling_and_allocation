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
    delete_queue = []
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


