from __future__ import annotations

import tkinter
from tkinter import ttk
from functools import partial
from tkinter import *
from typing import Callable, Any, TYPE_CHECKING
import re

from schedule.Tk import Scrolled
from schedule.Tk import InitGuiFontsAndColours as fac
from schedule.Tk import AdvancedTreeview
from schedule.Tk import MenuType
from schedule.Tk import DragNDropManager
from schedule.Tk import generate_menu
from schedule.Tk.menu_and_toolbars import MenuItem
from schedule.model import ResourceType

if TYPE_CHECKING:
    from schedule.model import Teacher, Lab, Stream

    RESOURCE_OBJECT = [Teacher | Lab | Stream]
    TREE_OBJECT = Any


def _default_menu(obj, parent_obj, iid, parent_iid) -> list[MenuItem]:
    menu = MenuItem(name=str(obj), label=str(obj), menu_type=MenuType.Command, command=lambda: None)
    return [menu, ]


def _default_resource_menu(resource_type: ResourceType, obj) -> list[MenuItem]:
    menu_title = MenuItem(name=str(resource_type), label=str(resource_type), menu_type=MenuType.Command,
                          command=lambda: None)
    menu = MenuItem(name=str(obj), label=str(obj), menu_type=MenuType.Command, command=lambda: None)
    return [menu_title, menu]


# =================================================================
# Edit courses GUI_Pages
# =================================================================

class EditCoursesTk:
    """A page that allows user to edit courses, assign resources, sections, blocks, etc

    event handlers
      1. ``handler_tree_edit``             edit the selected tree object (double click or return)
      2. ``handler_new_course``            create a new course (button)
      3. ``handler_tree_create_popup``      create a drop-down menu specific to the selected tree object (right click)
      4. ``handler_resource_create_menu``  create a drop-down menu specific to the selected resource object (right click)
      5. ``handler_show_teacher_stat``     no idea ??
      6. ``handler_drag_resource``         return true/false if dragged object is over a valid drop site
      7. ``handler_drop_resource``         drop dragged object onto source object

    :param frame: the frame to hold all the gui elements

    """
    colours: fac.TkColours = fac.colours
    Fonts: fac.TkFonts = fac.fonts
    Text_style_defn: dict[str, str] = {'bg': colours.WorkspaceColour, 'fg': colours.SelectedForeground}

    # ========================================================================
    # constructor
    # ========================================================================
    def __init__(self, frame: Frame):
        """create the EditCourse page
        :param frame: container object for the gui stuff
        """
        self.frame = frame

        # setup fonts if they have not already been set up
        if self.Fonts is None:
            self.Fonts = fac.TkFonts(frame.winfo_toplevel())

        # ----------------------------------------------------------------
        # call backs (should be defined by presenter)
        # ----------------------------------------------------------------
        self.handler_tree_edit: Callable[[TREE_OBJECT, TREE_OBJECT, str, str], None] \
            = lambda obj, parent_obj, tree_id, parent_id: print(f"Edit {str(obj)}")
        self.handler_new_course: Callable[[], None] = lambda: None
        self.handler_tree_create_popup: Callable[[TREE_OBJECT, TREE_OBJECT, str, str], list[MenuItem]] = _default_menu
        self.handler_resource_create_menu: Callable[
            [ResourceType, RESOURCE_OBJECT], list[MenuItem]] = _default_resource_menu
        self.handler_show_teacher_stat: Callable[[RESOURCE_OBJECT], None] = lambda obj: print(f"Teacher stat: {obj}")
        self.handler_drag_resource: Callable[[ResourceType, RESOURCE_OBJECT, TREE_OBJECT], bool] = \
            lambda resource_type, source_obj, target_obj: True
        self.handler_drop_resource: Callable[[ResourceType, RESOURCE_OBJECT, TREE_OBJECT], None] = \
            lambda resource_type, source_obj, target_obj: None

        # ----------------------------------------------------------------
        # create lists to keep track of widgets and objects for all resources
        # (teachers/streams/labs)
        # ----------------------------------------------------------------
        self.resource_Listbox: dict[ResourceType, Listbox] = dict()
        self.resource_objects: dict[ResourceType, list[RESOURCE_OBJECT]] = dict()
        for rt in ResourceType:
            self.resource_objects[rt] = list()

        # ----------------------------------------------------------------
        # using grid, create right and left panels
        # ----------------------------------------------------------------

        # remove anything that is already there
        for widget in frame.winfo_children():
            widget.destroy()

        # make panels
        right_panel = Frame(frame)
        right_panel.grid(row=0, column=1, sticky='nsew')
        left_panel = Frame(frame)
        left_panel.grid(row=0, column=0, sticky='nsew')

        # calculate min_width of left panel based on screen size
        width, height, _ = re.match(r"^=?(\d+)x(\d+)?([+-]\d+[+-]\d+)?$", frame.winfo_toplevel().geometry()).groups()

        # relative weights etc. to widths
        frame.grid_columnconfigure(0, minsize=int(0.5 * int(width)), weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------------------
        # make the gui contents
        # ----------------------------------------------------------------
        self.course_ttkTreeView = self._make_treeview(left_panel)
        self._make_resource_list_widgets(right_panel)
        self._make_button_row(right_panel)

        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=10, minsize=int(0.45 * int(height)))
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_rowconfigure(3, weight=0)

    # ###################################################################
    # Public Methods
    # ###################################################################
    def update_resource_type_objects(self, resource_type: ResourceType, objs: tuple[RESOURCE_OBJECT, ...]):
        """
        Updates the Listbox widget with Labs/Teachers/Streams string representations
        :param resource_type: what view resource_type are you updating?
        :param objs: all the objects that you want in the list
        """
        widget: Listbox = self.resource_Listbox[resource_type]
        widget.delete(0, 'end')
        self.resource_objects[resource_type].clear()
        for obj in objs:
            widget.insert('end', str(obj))
            self.resource_objects[resource_type].append(obj)

    def add_tree_item(self, parent_id: str, name: str, child: TREE_OBJECT, hide: bool = True) -> str:
        """add an object to the tree, as a child of the parent
        :param parent_id: an existing tree object that will become the parent of this new child
        :param name: the name of the child
        :param child: the child
        :param hide: hide the children?)
        :return: The id of the tree element
        """
        tag = "bold" if parent_id is None or parent_id == "" else "normal"
        parent_id = "" if parent_id is None else parent_id
        iid = self.course_ttkTreeView.insert_sorted(parent_id, child, text=name, tag=tag)
        self.course_ttkTreeView.after(20,lambda *_: self.course_ttkTreeView.item(parent_id, open=not hide))
        return iid

    def remove_tree_item(self, tree_iid: str):
        """remove an item from the tree
        :param tree_iid: the id of the item to be removed"""
        return self.course_ttkTreeView.delete(tree_iid)

    def remove_tree_item_children(self, tree_iid: str):
        """remove all children from the specified parent
        :param tree_iid: the id of the parent whose items are to be removed"""
        for child in self.course_ttkTreeView.get_children(tree_iid):
            self.course_ttkTreeView.delete(child)

    def update_tree_text(self, tree_iid: str, text: str):
        if self.course_ttkTreeView.exists(tree_iid):
            self.course_ttkTreeView.item(tree_iid, text=text)

    def clear_tree(self):
        """clear the tree of all items"""
        for child in self.course_ttkTreeView.get_children():
            self.course_ttkTreeView.delete(child)

    # ###################################################################
    # Events
    # ###################################################################

    def _cmd_double_click_teacher(self, e: tkinter.Event):
        """bound method for double click on a teacher object,
                calls handler: handler_show_teacher_stat
        """
        widget: Listbox = self.resource_Listbox[ResourceType.teacher]
        index = widget.nearest(e.y)
        widget.select_clear(0, 'end')
        widget.selection_set(index, index)
        obj = self.resource_objects[ResourceType.teacher][index]
        self.handler_show_teacher_stat(obj)

    def _cmd_edit_selection(self, *_):
        """bound method for <keypress Enter> or <double click> on treeview, or clicking 'Edit Selection' button
                calls handler: handler_tree_edit
        """

        # get the tree selected item
        iid_list = self.course_ttkTreeView.selection()
        if not iid_list:
            return
        obj = self.course_ttkTreeView.get_obj_from_id(iid_list[0])
        iid = iid_list[0]
        parent_iid = self.course_ttkTreeView.parent(iid)

        # get object associated with this item
        obj = self.course_ttkTreeView.get_obj_from_id(iid)
        parent_obj = self.course_ttkTreeView.get_obj_from_id(parent_iid)

        self.handler_tree_edit(obj,parent_obj,  iid, parent_iid)

    def _cmd_show_resource_type_menu(self, resource_type: ResourceType, e: tkinter.Event):
        """bound method for right click on resource list
                calls handler: handler_resource_create_menu
        """

        if resource_type is ResourceType.none:
            return
        widget: Listbox = self.resource_Listbox[resource_type]
        index = widget.nearest(e.y)
        widget.select_clear(0, 'end')
        widget.selection_set(index, index)
        obj = self.resource_objects[resource_type][index]

        # get menu info from callback routine
        menu = Menu(self.frame.winfo_toplevel(), tearoff=0)
        menu_details = self.handler_resource_create_menu(resource_type, obj)
        generate_menu(self.frame.winfo_toplevel(), menu_details, menu)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _new_course_btn_pressed(self, *_):
        """bound method for clicking 'new course' button
                calls handler: handler_new_course"""

        self.handler_new_course()

    def _cmd_show_tree_menu(self, e: tkinter.Event):
        """bound method for right click on tree item
                calls handler: handler_tree_create_popup
        """

        tv = self.course_ttkTreeView

        # which item was selected?
        iid = tv.identify_row(e.y)
        if not iid:
            return
        tv.selection_set(iid)
        parent_iid = tv.parent(iid)

        # get object associated with this item
        obj = tv.get_obj_from_id(iid)
        parent_obj = tv.get_obj_from_id(parent_iid)

        # get menu info from callback routine
        menu = Menu(self.frame.winfo_toplevel(), tearoff=0)
        menu_details = self.handler_tree_create_popup(obj, parent_obj, iid, parent_iid)
        generate_menu(self.frame.winfo_toplevel(), menu_details, menu)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _resource_on_start_drag(self, e: Event, info_data: dict) -> str:
        """bound event if a resource widget is about to be dragged from a resource listbox"""

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
        """bound event while the resource list object is being dragged around
                calls handler: handler_drag_resource"""

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
                target_obj: TREE_OBJECT = tv.get_obj_from_id(iid)
                source_obj: RESOURCE_OBJECT = info_data["source_obj"]
                resource_type: ResourceType = info_data["resource_type"]

                # check with 'user' if this is a valid item for dropping source onto target
                if self.handler_drag_resource(resource_type, source_obj, target_obj):
                    info_data["target_obj"] = target_obj
                    tv.selection_set(iid)
                    return True

        return False

    def _resource_on_drop(self, e: Event, info_data: dict, target: Widget):
        """bound event when a resource item is dropped
                calls handler: handler_drop_resource"""

        if self._resource_on_drag(e, info_data, target):
            target_obj: TREE_OBJECT = info_data["target_obj"]
            source_obj: RESOURCE_OBJECT = info_data["source_obj"]
            resource_type: ResourceType = info_data["resource_type"]
            self.handler_drop_resource(resource_type, source_obj, target_obj)

    # ###################################################################
    # Private Methods
    # ###################################################################

    def _make_treeview(self, left_panel: Frame):
        """make tree representing all courses, sections, blocks, resources"""
        style = ttk.Style()
        style.configure('Treeview', rowheight=25)  # Adjust '30' to your desired height
        tree_scrolled: Scrolled = Scrolled(left_panel, 'AdvancedTreeview', scrollbars='se')
        tree_scrolled.pack(expand=1, fill='both', side='left')
        tv: AdvancedTreeview = tree_scrolled.widget
        tv.bind('<Double-1>', self._cmd_edit_selection)
        tv.bind('<Key-Return>', self._cmd_edit_selection)
        tv.tag_configure("bold", font=self.Fonts.big)
        tv.tag_configure("normal", font=self.Fonts.normal)
        tv.bind('<ButtonRelease-2>', self._cmd_show_tree_menu)
        tv.bind('<ButtonRelease-3>', self._cmd_show_tree_menu)

        return tv

    def _make_resource_list_widgets(self, panel):
        """make a list widget for teachers/labs/streams"""

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

        # Set up binding for menus and dragging-n-dropping
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

    def _make_button_row(self, panel: Frame):
        """make the button row for creating new courses, editing selections, etc"""
        button_row = Frame(panel)
        button_row.grid(column=0, sticky='nsew', row=3)
        btn_new_course = Button(button_row, text="New Course", width=11,
                                command=lambda: self._new_course_btn_pressed())
        btn_new_course.pack(side='left')
        btn_edit_selection = Button(button_row, text="Edit Selection", width=11,
                                    command=lambda: self._cmd_edit_selection())
        btn_edit_selection.pack(side='left')
