from __future__ import annotations

import tkinter
from functools import partial
from tkinter import *
from typing import Callable, Any
import re

from schedule.Tk.Scrolled import Scrolled
import schedule.Tk.InitGuiFontsAndColours as fac
from schedule.Tk.AdvancedTreeview import AdvancedTreeview
from schedule.Model.ScheduleEnums import ResourceType
from schedule.UsefulClasses.MenuItem import MenuItem, MenuType
from schedule.Tk.DragNDrop import DragNDropManager
from ..GUI_Pages.MenuAndToolBarTk import generate_menu


def _default_menu(obj) -> list[MenuItem]:
    menu = MenuItem(name=str(obj), label=str(obj), menu_type=MenuType.Command, command=lambda: None)
    return [menu, ]


def _default_resource_menu(resource_type: ResourceType, obj) -> list[MenuItem]:
    menu_title = MenuItem(name=str(resource_type), label=str(resource_type), menu_type=MenuType.Command,
                          command=lambda: None)
    menu = MenuItem(name=str(obj), label=str(obj), menu_type=MenuType.Command, command=lambda: None)
    return [menu_title, menu]


# =================================================================
# Edit courses GUI_Pages
# - inserts widgets into a gui container (frame)
# -----------------------------------------------------------------
# INPUTS:
#   frame               # must be empty!!
#
# METHODS:
#   alert               ()
#   add                 (tree_path)
#   course_style        ()
#   delete              (type_of_delete, path)
#   set_labs            (array of {-id=>lab_id, -name=>lab_number})
#   set_streams         (array of {-id=>stream_id, -name=>{stream_name})
#   show_message        (title, message)
#   update_tree_text    (tree_path, new_text)
#
# RETURNS:
#   - nothing -
#
# REQUIRED EVENT HANDLERS:
#   cb_object_dropped_on_tree       (type_of_object_dropped, id_of_dropped_object, tree_path, target_object)
#   cb_edit_obj                     (object_to_edit, tree_path)
#   cb_get_view_type_menu_info     (teacher_lab_stream_id, resource_type)
#   cb_get_tree_menu                (selected_object, parent_object, tree_path)
#   cb_new_course                   ()
#   cb_show_teacher_stat            (teacher_id)
# =================================================================

class EditCoursesTk:
    colours: fac.TkColours = fac.colours
    Fonts: fac.TkFonts = fac.fonts
    Text_style_defn: dict[str, str] = {'bg': colours.WorkspaceColour, 'fg': colours.SelectedForeground}

    # ========================================================================
    # constructor
    # ========================================================================
    def __init__(self, frame: Frame):
        self.frame = frame

        # setup fonts if they have not already been set up
        if self.Fonts is None:
            self.Fonts = fac.TkFonts(frame.winfo_toplevel())

        # keep track of widgets and objects for all resources
        # (teachers/streams/labs)
        self.resource_Listbox: dict[ResourceType, Listbox] = dict()
        self.resource_objects: dict[ResourceType, list[Any]] = dict()
        for rt in ResourceType:
            self.resource_objects[rt] = list()

        # call back routines
        self.cb_edit_obj: Callable[[Any], None] = lambda obj: print(f"Edit {str(obj)}")
        self.cb_new_course: Callable[[], None] = lambda: None
        self.cb_get_tree_menu: Callable[[Any], list[MenuItem]] = _default_menu
        self.cb_get_resource_menu: Callable[[ResourceType, Any], list[MenuItem]] = _default_resource_menu
        self.cb_show_teacher_stat: Callable[[Any], None] = lambda obj: print(f"Teacher stat: {obj}")
        self.cb_target_is_valid_drop_site: [[ResourceType, Any, Any], bool] = \
            lambda resource_type, source_obj, target_obj: True
        self.cb_dropped_resource_onto_course_item: [[ResourceType, Any, Any], None] = \
            lambda resource_type, source_obj, target_obj: None

        # ----------------------------------------------------------------
        # using grid, create right and left panels
        # ----------------------------------------------------------------

        # remove anything that is already there
        for widget in frame.grid_slaves():
            widget.destroy()
        for widget in frame.pack_slaves():
            widget.destroy()

        # make panels
        right_panel = Frame(frame)
        right_panel.grid(row=0, column=1, sticky='nsew')
        left_panel = Frame(frame)
        left_panel.grid(row=0, column=0, sticky='nsew')

        # calculate min_width of left panel based on screen size
        width, _, _ = re.match(r"^=?(\d+)x(\d+)?([+-]\d+[+-]\d+)?$", frame.winfo_toplevel().geometry()).groups()
        min_width = int(7.0 / 16.0 * int(width))

        # relative weights etc. to widths
        frame.grid_columnconfigure(0, minsize=min_width, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------------------
        # make the gui contents
        # ----------------------------------------------------------------
        self.course_ttkTreeView = self._make_treeview(left_panel)
        self._make_resource_list_widgets(right_panel)
        self._make_button_row(right_panel)

        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=2)
        right_panel.grid_rowconfigure(2, weight=2)
        right_panel.grid_rowconfigure(3, weight=0)

    # ===================================================================
    # update data
    # ===================================================================
    def update_resource_type_objects(self, resource_type: ResourceType, objs: list[Any]):
        """
        Updates the Listbox widget with Labs/Teachers/Streams string representations
        :param resource_type: what view resource_type are you updating?
        :param objs: all the objects that you want in the list
        """
        widget: Listbox = self.resource_Listbox[resource_type]
        widget.delete(0, 'end')
        self.resource_objects[resource_type].clear()
        for i, obj in enumerate(objs):
            widget.insert('end', str(obj))
            self.resource_objects[resource_type].append(obj)

    def add_tree_item(self, parent: str, name: str, obj: Any) -> str:
        tag = "bold" if parent is None or parent == "" else "normal"
        return self.course_ttkTreeView.insert_sorted(parent, obj, text=name, tag=tag)

    def remove_tree_item(self, tree_iid: str):
        return self.course_ttkTreeView.delete(tree_iid)

    def clear_tree(self):
        return self.course_ttkTreeView.delete(self.course_ttkTreeView.get_children(""))

    # ===================================================================
    # make the tree view
    # ===================================================================
    def _make_treeview(self, left_panel: Frame):
        tree_scrolled: Scrolled = Scrolled(left_panel, 'AdvancedTreeview', scrollbars='se')
        tree_scrolled.pack(expand=1, fill='both', side='left')
        tv: AdvancedTreeview = tree_scrolled.widget
        tv.bind('<Double-1>', self._cmd_edit_selection)
        tv.bind('<Key-Return>', self._cmd_edit_selection)
        tv.tag_configure("bold", font=self.Fonts.bold)
        tv.tag_configure("normal", font=self.Fonts.normal)
        tv.bind('<Button-2>', self._cmd_show_tree_menu)
        return tv

    # ===================================================================
    # make resource list widgets
    # ===================================================================
    def _make_resource_list_widgets(self, panel):
        # ---------------------------------------------------------------
        # teacher and lab and stream list
        # ---------------------------------------------------------------
        # the scrolled method requires an empty frame, or else, it messes up.
        f = Frame(panel)
        f.grid(column=0, stick='nsew', row=0)
        Label(f, text="Teachers", font=self.Fonts.bold).pack()
        sf = Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='e')
        s.widget.bind('<Double-Button-1>', self._cmd_double_click_teacher)
        self.resource_Listbox[ResourceType.teacher] = s.widget

        f = Frame(panel)
        f.grid(column=0, stick='nsew', row=1)
        Label(f, text="Labs", font=self.Fonts.bold).pack()
        sf = Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='e')
        self.resource_Listbox[ResourceType.lab] = s.widget

        f = Frame(panel)
        f.grid(column=0, stick='nsew', row=2)
        Label(f, text="Streams", font=self.Fonts.bold).pack()
        sf = Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='e')
        self.resource_Listbox[ResourceType.stream] = s.widget

        # ---------------------------------------------------------------
        # Set up binding for menus and dragging-n-dropping
        # ---------------------------------------------------------------
        dm = DragNDropManager()

        for resource_type in ResourceType:
            if resource_type not in self.resource_Listbox:
                continue
            dm.add_draggable(self.resource_Listbox[resource_type],
                             on_start=self._resource_on_start_drag,
                             on_drop=self._resource_on_drop,
                             on_drag=self._resource_on_drag)

            self.resource_Listbox[resource_type].bind(
                '<Button-2>',
                partial(self._cmd_show_resource_type_menu, resource_type))

            self.resource_Listbox[resource_type].unbind('<Motion>')

    # ==================================================================
    # make the button row for creating new courses, editing selections, etc
    # ==================================================================
    def _make_button_row(self, panel: Frame):
        button_row = Frame(panel)
        button_row.grid(column=0, sticky='nsew', row=3)
        btn_new_course = Button(button_row, text="New Course", width=11,
                                command=lambda *args: self.cb_new_course(*args))
        btn_new_course.pack(side='left')
        btn_edit_selection = Button(button_row, text="Edit Selection", width=11,
                                    command=lambda *args: self._cmd_edit_selection(*args))
        btn_edit_selection.pack(side='left')

    # ==================================================================
    # bound method for right click on resource list
    # ==================================================================
    def _cmd_show_resource_type_menu(self, resource_type: ResourceType, e: tkinter.Event):
        if resource_type is ResourceType.none:
            return
        widget: Listbox = self.resource_Listbox[resource_type]
        index = widget.nearest(e.y)
        widget.select_clear(0, 'end')
        widget.selection_set(index, index)
        obj = self.resource_objects[resource_type][index]

        # get menu info from callback routine
        menu = Menu(self.frame.winfo_toplevel(), tearoff=0)
        menu_details = self.cb_get_resource_menu(resource_type, obj)
        generate_menu(self.frame.winfo_toplevel(), menu_details, menu)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    # ==================================================================
    # bound method for right click on tree item
    # ==================================================================
    def _cmd_show_tree_menu(self, e: tkinter.Event):
        tv = self.course_ttkTreeView

        # which item was selected?
        iid = tv.identify_row(e.y)
        if not iid:
            return
        tv.selection_set(iid)

        # get object associated with this item
        obj = tv.get_obj_from_id(iid)

        # get menu info from callback routine
        menu = Menu(self.frame.winfo_toplevel(), tearoff=0)
        menu_details = self.cb_get_tree_menu(obj)
        generate_menu(self.frame.winfo_toplevel(), menu_details, menu)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    # =================================================================
    # bound method for <Enter> on treeview, or clicking 'Edit Selection' button
    # =================================================================
    def _cmd_edit_selection(self, *_):
        iid_list = self.course_ttkTreeView.selection()
        if not iid_list:
            return
        obj = self.course_ttkTreeView.get_obj_from_id(iid_list[0])
        self.cb_edit_obj(obj)

    # =================================================================
    # event handler for double clicking a teacher
    # =================================================================
    def _cmd_double_click_teacher(self, e: tkinter.Event):
        widget: Listbox = self.resource_Listbox[ResourceType.teacher]
        index = widget.nearest(e.y)
        widget.select_clear(0, 'end')
        widget.selection_set(index, index)
        obj = self.resource_objects[ResourceType.teacher][index]
        print("double clicked teacher")
        self.cb_show_teacher_stat(obj)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Drag and Drop stuff
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def _resource_on_start_drag(self, e: Event, info_data: dict) -> str:
        """Executed if a resource widget is about to be dragged from a resource listbox"""

        # what resource type is it?
        info_data["resource_type"] = ResourceType.none
        lb: Listbox = e.widget
        rtype: ResourceType = ResourceType.none
        for rt in self.resource_Listbox:
            if lb == self.resource_Listbox[rt]:
                rtype = rt

        # select the nearest item in the list
        index = lb.nearest(e.y)
        lb.select_clear(0, 'end')
        lb.selection_set(index, index)

        # save some info for later use
        info_data["source_obj"] = self.resource_objects[rtype][index]
        info_data["resource_type"] = rtype

        # return string to be used in the drag indicator
        return lb.get(index)

    def _resource_on_drag(self, e: Event, info_data: dict, target: Widget) -> bool:
        """Executed while the resource list object is being dragged around"""

        tv = self.course_ttkTreeView
        for s_iid in tv.selection():
            tv.selection_remove(s_iid)

        # a resource widget can only be dropped on the serl.course_ttkTreeView
        if target == tv:

            # get position of mouse within the treeview widget, and identify item in treeview under mouse
            tv_y_pos = e.y_root - tv.winfo_rooty()
            iid = tv.identify_row(tv_y_pos)

            # if we have a valid id...
            if iid:
                tv.item(iid, open=True)
                target_obj = tv.get_obj_from_id(iid)
                source_obj = info_data["source_obj"]
                resource_type = info_data["resource_type"]

                # check with 'user' if this is a valid item for dropping source onto target
                if self.cb_target_is_valid_drop_site(resource_type, source_obj, target_obj):
                    info_data["target_obj"] = target_obj
                    tv.selection_set(iid)
                    return True

        return False

    def _resource_on_drop(self, e: Event, info_data: dict, target: Widget):
        """Called when a resource item is dropped"""

        if self._resource_on_drag(e, info_data, target):
            target_obj = info_data["target_obj"]
            source_obj = info_data["source_obj"]
            resource_type = info_data["resource_type"]
            self.cb_dropped_resource_onto_course_item(resource_type, source_obj, target_obj)
