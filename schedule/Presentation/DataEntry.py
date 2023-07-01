from time import sleep
from typing import Any, Optional

from ..Schedule.Schedule import Schedule
from ..Presentation.globals import set_dirty_flag
from ..GUI_Pages.DataEntryTk import DataEntryTk, DEColumnDescription
from ..Schedule.ScheduleEnums import ViewType

property_conversions_from_str = {
    "id": lambda x: int(x) if x else 0,
    "firstname": lambda x: x,
    "lastname": lambda x: x,
    "release": lambda x: float(x) if x else 0,
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
    def __init__(self, frame, view_type: ViewType, schedule: Optional[Schedule], test_gui=None):
        """
        Creates the basic DataEntry (a simple matrix)
        :param frame: gui container object
        :param view_type: Is it a lab, stream or teacher
        :param schedule: The Schedule object
        """
        if not test_gui:
            self.gui = DataEntryTk(frame, self._cb_delete_obj, self._cb_save)
        else:
            self.gui = test_gui

        self.delete_queue = list()
        self.view_type = view_type
        self.schedule = schedule
        self.column_descriptions: list[DEColumnDescription] = [
            DEColumnDescription(title="No Schedule", width=40, property="")
        ]

        # ---------------------------------------------------------------
        # what are the columns?
        # ---------------------------------------------------------------
        if self.view_type == ViewType.teacher:
            self.column_descriptions = [
                DEColumnDescription(title="ID", width=4, property="id"),
                DEColumnDescription(title="First Name", width=20, property="firstname"),
                DEColumnDescription(title="Last Name", width=20, property="lastname"),
                DEColumnDescription(title="RT", width=8, property="release"),
            ]

        elif self.view_type is ViewType.lab:
            self.column_descriptions = [
                DEColumnDescription(title="ID", width=4, property="id"),
                DEColumnDescription(title="Room", width=7, property="number"),
                DEColumnDescription(title="Description", width=40, property="description"),
            ]

        elif self.view_type is ViewType.stream:
            self.column_descriptions = [
                DEColumnDescription(title="ID", width=4, property="id"),
                DEColumnDescription(title="Number", width=10, property="number"),
                DEColumnDescription(title="Name", width=40, property="description"),
            ]

        self.gui.initialize_columns(self.column_descriptions)

    # =================================================================
    # refresh the tables
    # =================================================================
    def refresh(self):
        objs = tuple()
        data = list()

        if self.schedule is None:
            self.gui.refresh(data)

        if self.view_type == ViewType.lab:
            objs = self.schedule.labs
        elif self.view_type == ViewType.stream:
            objs = self.schedule.streams
        elif self.view_type == ViewType.teacher:
            objs = self.schedule.teachers

        # Create a 2-d array of the data that needs to be displayed.
        for obj in objs:
            row = list()
            for column in self.column_descriptions:
                row.append(str(get_set_property(obj, column.property)))
            data.append(row)

        # refresh the GUI_Pages
        self.gui.refresh(data)

        # purge the delete queue
        self.delete_queue = list()

    # =================================================================
    # Callbacks
    # =================================================================

    # ------------------------------------------------------------------------
    # adding a ViewType object to the schedule
    # ------------------------------------------------------------------------
    def __add_obj(self, data: dict):
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
    def _cb_save(self, *_):
        """Save any changes that the user entered in the GUI_Pages form."""
        any_changes = False

        # Get data from the GUI_Pages object.
        all_data = self.gui.get_all_data()

        # Just in case saving is already in progress,
        # wait before continuing.
        if DataEntry.Currently_saving > 2:
            return  # 2 is too many.
        if DataEntry.Currently_saving:
            sleep(2)
        DataEntry.Currently_saving += 1

        # Read data from the data object.
        for data in all_data:
            if not len([x for x in data if x]):
                continue

            # --------------------------------------------------------------------
            # if this row has an ID, then we need to update the
            # corresponding object
            # --------------------------------------------------------------------
            if data[self.Id_index] and data[self.Id_index] != '':
                obj_id = int(data[self.Id_index])
                obj = self.schedule.get_view_type_obj_by_id(self.view_type, obj_id)

                # Loop over each method used to get_by_id info about this object.
                for col, column in enumerate(self.column_descriptions):
                    if col == self.Id_index:
                        continue

                    # check if data has changed
                    if str(get_set_property(obj, column.property)) != data[col]:
                        value = property_conversions_from_str[column.property](data[col])
                        get_set_property(obj, column.property, value, set_flag=True)
                        any_changes = True

            # --------------------------------------------------------------------
            # if this row does not have an ID, then we need to create
            # corresponding object
            # --------------------------------------------------------------------
            else:
                any_changes = True
                new_data = dict()
                for col, column in enumerate(self.column_descriptions):
                    if col == self.Id_index:
                        continue
                    new_data[column.property] = property_conversions_from_str[column.property](data[col])
                self.__add_obj(new_data)

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

        # if there have been changes, set global dirty flag
        if any_changes:
            set_dirty_flag()

        # all done saving, decrement number of files currently being saved
        DataEntry.Currently_saving -= 1
        self.refresh()

    # =================================================================
    # delete object
    # =================================================================
    def _cb_delete_obj(self, row_data: list[str]):
        """Save delete requests, to be processed later."""
        obj = None
        if row_data[self.Id_index] and row_data[self.Id_index] != '':
            obj_id = int(row_data[self.Id_index])
            obj = self.schedule.get_view_type_obj_by_id(self.view_type, obj_id)
        if obj:
            self.delete_queue.append(obj)


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
