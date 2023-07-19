from __future__ import annotations
from tkinter import *
from tkinter import ttk
from typing import Callable, Any, Optional

from ..Tk.Scrolled import Scrolled
from tkinter.font import Font
import schedule.Tk.InitGuiFontsAndColours as fac
from schedule.Schedule.ScheduleEnums import ResourceType
import re


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

    def __init__(self, frame: Frame):
        self._frame: Frame = frame
        self._toggle = None
        self._dropped = None

        self.view_type_objects: dict[ResourceType, list[Any]] = dict()
        for view_type in ResourceType:
            self.view_type_objects[view_type] = list()

        self.cb_edit_obj: Callable[[Any, id], None] = lambda obj, obj_id: None
        self.cb_new_course: Callable[[str, str], None] = lambda name, description: None
        self.cb_get_tree_menu: Callable[[Any, id], list] = lambda obj, obj_id: list()

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
        # make Schedule course_ttkTreeView
        # ----------------------------------------------------------------
        tree_scrolled: Scrolled = Scrolled(left_panel, 'Treeview', scrollbars='se')
        tree_scrolled.pack(expand=1, fill='both', side='left')
        self.course_ttkTreeView: ttk.Treeview = tree_scrolled.widget
        self.course_ttkTreeView.bind('<Double-1>', self._cmd_edit_selection)
        self.course_ttkTreeView.bind('<Key-Return>', self._cmd_edit_selection)

        # ----------------------------------------------------------------
        # make panel for teachers/labs/streams
        # ----------------------------------------------------------------
        self._subdivide_right_panel(right_panel)

        # # -------------------------------
        # # Right click menu binding
        # # -------------------------------
        # self._create_right_click_menu(tree_scrolled)
        #
        # # ----------------------------------------------------------------
        # # drag and drop bindings
        # # ----------------------------------------------------------------
        # self._create_drag_drop_objs()

    # ===================================================================
    # update data
    # ===================================================================
    def update_view_type_objects(self, view_type: ResourceType, objs: list[Any]):
        """
        Updates the Listbox widget with Labs/Teachers/Streams string representations
        :param view_type: what view resource_type are you updating?
        :param objs: all the objects that you want in the list
        """
        widget: Listbox = self.view_type_tk_lists[view_type]
        widget.delete(0, 'end')
        self.view_type_objects[view_type].clear()
        for i, obj in enumerate(objs):
            widget.insert('end', str(obj))
            self.view_type_objects[view_type].append(obj)

    def update_courses_tree(self, objects: list[TreeViewObjectType], parent: str = ""):
        """
        Redraws the treeview widget with all the data for each course
        :param objects: a list of objects, and sub objects
        :param parent: define which treeview item is the parent, "" is top level
        """
        self.course_ttkTreeView.delete(*self.course_ttkTreeView.get_children())
        self.tree_objects.clear()
        self._update_courses_tree(objects)

    def update_single_course(self, tv_course_to_update: TreeViewObjectType):
        """If course exists, update all streams/teachers, etc"""

        course_to_modify = tv_course_to_update.schedule_obj
        course_specifics = tv_course_to_update.children

        new_tree_id = None
        for row, tree_id in enumerate(self.course_ttkTreeView.get_children()):

            # does the object already exist in the tree, or do we need to insert?
            if self.tree_objects[tree_id] == course_to_modify:
                for branch in self.course_ttkTreeView.get_children(tree_id):
                    self._prune(tree_id)
                new_tree_id = tree_id
                break

            # the course does not exist, so we put it here
            if self.tree_objects[tree_id] > course_to_modify:
                new_tree_id = self.course_ttkTreeView.insert("", index=row)
                break

        # the course does not exist, so we put it here
        if new_tree_id is None:
            new_tree_id = self.course_ttkTreeView.insert("", index='end')

        self._update_courses_tree(tv_course_to_update.children, new_tree_id)
        self._expand_whole_branch(new_tree_id)
        return

    def _update_courses_tree(self, objects: list[TreeViewObjectType], parent: str = ""):
        for tv_obj in objects:
            tree_id = self.course_ttkTreeView.insert(parent, 'end', text=str(tv_obj.schedule_obj))
            self.tree_objects[tree_id] = tv_obj.schedule_obj
            self.update_courses_tree(tv_obj.children, tree_id)

    def _prune(self, tree_id: str):
        """Not only remove the tree branch, but remove the data from tree_objects as well"""
        for twig in self.course_ttkTreeView.get_children(tree_id):
            self._prune(twig)
        self.tree_objects.pop(tree_id, None)

    def _expand_whole_branch(self, tree_id: str):
        """Opens all the twigs in this branch"""
        self.course_ttkTreeView.item(tree_id, open=True)
        for twig in self.course_ttkTreeView.get_children(tree_id):
            self._expand_whole_branch(twig)

    # ===================================================================
    # create panel for modifying the schedule
    # ===================================================================
    def _subdivide_right_panel(self, panel):

        # ---------------------------------------------------------------
        # button row
        # ---------------------------------------------------------------
        button_row = Frame(panel)
        button_row.grid(column=0, sticky='nsew', row=3)

        # ---------------------------------------------------------------
        # buttons
        # ---------------------------------------------------------------
        btn_new_course = Button(button_row, text="New Course", width=11, command=self.cb_new_course)
        btn_new_course.pack(side='left')

        btn_edit_selection = Button(button_row, text="Edit Selection", width=11, command=self._cmd_edit_selection)
        btn_edit_selection.pack(side='left')

        # ---------------------------------------------------------------
        # teacher and lab and stream list
        # ---------------------------------------------------------------
        # the scrolled method requires an empty frame, or else, it messes up.
        f = Frame(panel)
        f.grid(column=0, stick='nsew', row=0)
        s: Scrolled = Scrolled(f, 'Listbox', scrollbars='e')
        self.view_type_tk_lists[ResourceType.teacher] = s.widget

        f = Frame(panel)
        f.grid(column=0, stick='nsew', row=1)
        s: Scrolled = Scrolled(f, 'Listbox', scrollbars='e')
        self.view_type_tk_lists[ResourceType.lab] = s.widget

        f = Frame(panel)
        f.grid(column=0, stick='nsew', row=2)
        s: Scrolled = Scrolled(f, 'Listbox', scrollbars='e')
        self.view_type_tk_lists[ResourceType.stream] = s.widget

        # self.view_type_tk_lists[ResourceType.teacher].bind('<Double-Button-1>', self._cmd_double_click_teacher)
        #
        # # ---------------------------------------------------------------
        # # unbind the motion for general listbox widgets, which interferes
        # # with the drag-drop bindings later on.
        # # ---------------------------------------------------------------
        # for view_type in ResourceType:
        #     self.view_type_tk_lists[view_type].bind('<B1-Motion>', None)
        #
        # # ---------------------------------------------------------------
        # # assign weights to the panel grid
        # # ---------------------------------------------------------------
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=2)
        panel.grid_rowconfigure(2, weight=2)
        panel.grid_rowconfigure(3, weight=0)

    # ==================================================================
    # create all the right click menu stuff
    # ==================================================================
    def _create_right_click_menu(self, scrolled_tree):
        # TODO: what is lab_menu and stream_menu for if not saved?
        lab_menu = Menu(self.view_type_tk_lists[ResourceType.lab], tearoff=0)
        stream_menu = Menu(self.view_type_tk_lists[ResourceType.stream], tearoff=0)

        for view_type in ResourceType:
            self.view_type_tk_lists[view_type].bind(
                '<Button-2>',
                lambda e: self._cmd_show_view_type_menu(view_type, e))

        self.course_ttkTreeView.bind('<Button-2>', self._cmd_show_tree_menu())

    # TODO: create callback routines
    def _cmd_show_view_type_menu(self, *_):
        pass

    def _cmd_show_tree_menu(self, *_):
        pass

    def _cmd_edit_selection(self, *_):
        pass

    def _cmd_double_click_teacher(self, *_):
        pass


#     # ==================================================================
#     # show pop-up course_ttkTreeView menu
#     # ==================================================================
#     def _cmd_show_tree_menu(self, e: Event):
#         course_ttkTreeView: ttk.Treeview = self.course_ttkTreeView
#
#         # which entity was selected (based on mouse position), and set_default_fonts_and_colours focus and selection
#         entity_id = course_ttkTreeView.identify_row(e.y)
#         if not entity_id:
#             return
#         course_ttkTreeView.selection_clear()
#         course_ttkTreeView.selection_set(entity_id)
#         course_ttkTreeView.focus(entity_id)
#
#         # get_by_id the object and notebook object associated with the selected item,
#         # if no notebook (i.e. Schedule) we don't need a drop-down menu
#         parent = self._get_parent(entity_id)
#         if not parent:
#             return
#
#         # create the drop-down menu
#         menu_array: list[str] = self.cb_get_tree_menu(self.__tree_objs[entity_id])
#         tree_menu = Menu(self.course_ttkTreeView, tearoff=0, menuitems=menu_array)
#         '''
#     my $menu_array = $self->cb_get_tree_menu->( $obj, $parent_obj, $path );
#     my $tree_menu = $course_ttkTreeView->Menu( -tearoff => 0, -menuitems => $menu_array );
#     $tree_menu->post( $x, $y );
# }
'''

    def _cmd_show_view_type_menu(self, menu_type: str, e: Event):
        pass

    def _cmd_double_click_teacher(self, teachers_list: list[object], e: Event):
        pass

    # =================================================================
    # get_by_id the parents of a particular object
    # =================================================================
    def get_parents(self, tree_item_id: str) -> list[object]:
        return list(self._get_parent(self.course_ttkTreeView.parent(tree_item_id)))

    def _get_parent(self, tree_item_id: str):
        while tree_item_id != "":
            yield tree_item_id
            tree_item_id = self.course_ttkTreeView.parent(tree_item_id)

    # =================================================================
    # Callback functions
    # =================================================================
    def _cmd_edit_selection(self, *args) -> None:
        tree_item_id = self.course_ttkTreeView.focus()
        obj = self.__tree_objs[tree_item_id]
        self.cb_edit_obj(obj, tree_item_id)

    # =================================================================
    # create all the drag'n'drop stuff
    # =================================================================
    def _create_drag_drop_objs(self):

        # -------------------------------------------------------------
        # drag from teacher_ids/lab_ids to course course_ttkTreeView
        # -------------------------------------------------------------
        pass


'''
