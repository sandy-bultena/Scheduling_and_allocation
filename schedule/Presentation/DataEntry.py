
from time import sleep
from typing import Any, Optional, Callable

from ..Schedule.Schedule import Schedule
from ..Presentation.globals import set_dirty_flag
from ..GUI.DataEntryTk import DataEntryTk
from ..Schedule.ScheduleEnums import ViewType

property_conversions_from_str = {
    "id": lambda x: int(x),
    "firstname": lambda x: x,
    "lastname": lambda x: x,
    "release": lambda x: float(x),
    "number": lambda x: x,
    "description": lambda x: x
}


def get_set_property(obj, property_name: str, value: Any = None, set_flag=False):
    """dynamically set attributes and properties"""
    f = getattr(obj, property_name, None)
    if f is None:
        return None
    if not set_flag:
        return f
    else:
        setattr(obj, property_name, value)


class DataEntry:
    # =================================================================
    # Class Variables
    # =================================================================
    Id_index = 0
    Currently_saving = 0

    # =================================================================
    # new
    # =================================================================
    def __init__(self, gui: DataEntryTk, view_type: ViewType, view_type_objs: list,
                 schedule: Schedule):
        """
        Creates the basic DataEntry (a simple matrix)
        :param view_type: Is it a lab, stream or teacher
        :param view_type_objs: the objects to be displayed
        :param schedule: the schedule
        """
        self.delete_queue = list()
        self.view_type = view_type
        self.objs = view_type_objs
        self.schedule = schedule
        self.gui = gui
        self._col_methods: list[Callable[[Any, Optional[str]], None]]
        self.col_titles = ['invalid viewType']
        self.col_widths = [40]

        # ---------------------------------------------------------------
        # what are the columns?
        # ---------------------------------------------------------------
        if self.view_type == ViewType.teacher:
            self._col_get_methods = ['id', 'firstname', 'lastname', 'release']
            self.col_titles = ["id", 'first name', 'last name', 'RT']
            self.col_widths = [4, 20, 20, 8]

        elif self.view_type is ViewType.lab:
            self._col_property_names = ['id', 'number', 'description']
            self.col_titles = ["id", 'room', 'title']
            self.col_widths = [4, 7, 40]

        elif self.view_type is ViewType.stream:
            self._col_property_names = ['id', 'number', 'description']
            self.col_titles = ['id', 'number', 'title']
            self.col_widths = [4, 10, 40]

        self.refresh()

    # =================================================================
    # refresh the tables
    # =================================================================
    def refresh(self):

        # Create a 2-d array of the data that needs to be displayed.
        data = list()
        for obj in self.objs:
            row = list()
            for col_property in self._col_property_names:
                row.append(str(get_set_property(obj, col_property)))
            data.append(row)

        # refresh the GUI
        self.gui.refresh(data)

        # purge the delete queue
        self.delete_queue = list()

    # =================================================================
    # Callbacks
    # =================================================================

    # ------------------------------------------------------------------------
    # adding a ViewType object to the schedule
    # ------------------------------------------------------------------------
    def add_obj(self, data: dict):
        if self.view_type == ViewType.teacher:
            teacher = self.schedule.add_teacher(firstname=data["firstname"],
                                                lastname=data["lastname"])
            teacher.release = data["release"]
        elif self.view_type == ViewType.lab:
            self.schedule.add_lab(number=data["number"],
                                  description=data["description"])
        elif self.view_type == ViewType.stream:
            self.schedule.add_stream(number=data["number"],
                                     description=data["description"])

    # ------------------------------------------------------------------------
    # Save updated data
    # ------------------------------------------------------------------------
    def _cb_save(self):
        """Save any changes that the user entered in the GUI form."""
        schedule = self.schedule
        any_changes = False

        # Get data from the GUI object.
        all_data = self.gui.get_all_data()

        # Just in case saving is already in progress,
        # wait before continuing.
        if DataEntry.Currently_saving > 2:
            return  # 2 is too many.
        if DataEntry.Currently_saving:
            sleep(2)
        DataEntry.Currently_saving += 1

        # Read data from the data object.
        for row in all_data:
            data = row.copy()

            # --------------------------------------------------------------------
            # if this row has an ID, then we need to update the
            # corresponding object
            # --------------------------------------------------------------------
            if data[self.Id_index] and data[self.Id_index] != '':
                obj_id = int(data[self.Id_index])
                obj = self.schedule.get_view_type_obj_by_id(self.view_type, obj_id)

                # Loop over each method used to get_by_id info about this object.
                for col, property_name in enumerate(self._col_property_names):
                    if col == self.Id_index:
                        continue

                    # check if data has changed
                    if str(get_set_property(obj, property_name)) != data[col]:
                        value = property_conversions_from_str[property_name](data[col])
                        get_set_property(obj, property_name, value, set_flag=True)
                        any_changes = True

            # --------------------------------------------------------------------
            # if this row does not have an ID, then we need to create
            # corresponding object
            # --------------------------------------------------------------------
            else:
                any_changes = True
                new_data = dict()
                for col, property_name in enumerate(self._col_property_names):
                    if col == self.Id_index:
                        continue
                    new_data['property_name'] = property_conversions_from_str[property_name](data[col])
                self.add_obj(new_data)

        # ------------------------------------------------------------------------
        # go through delete queue and apply changes
        # ------------------------------------------------------------------------
        while len(self.delete_queue) > 0:
            any_changes = True
            obj = self.delete_queue.pop()
            if self.view_type == ViewType.teacher:
                self.schedule.remove_teacher(obj)
            elif self.view_type == ViewType.lab:
                self.schedule.remove_lab(obj)
            elif self.view_type == ViewType.stream:
                self.schedule.remove_stream(obj)

        # if there have been changes, set_default_fonts_and_colours global dirty flag and do what is necessary.
        if any_changes:
            set_dirty_flag()
        DataEntry.Currently_saving -= 1

    # =================================================================
    # delete object
    # =================================================================
    def _cb_delete_obj(self, data):
        """Save delete requests, to be processed later."""

        # Create a queue so we can delete the objects when the new info is saved.
        obj = self.schedulable_list_obj.get_by_id(data[DataEntry.Id_index])
        if obj:
            self.delete_queue.extend([self.schedulable_list_obj, obj])


'''
=head1 AUTHOR
Sandy Bultena, Ian Clement, Jack Burns. Converted to Python by Evan Laverdiere.
=head1 COPYRIGHT
Copyright (c) 2020, Jack Burns, Sandy Bultena, Ian Clement. 
All Rights Reserved.
This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License
     (see http://www.perl.com/perl/misc/Artistic.html)
=cut

1;

'''
