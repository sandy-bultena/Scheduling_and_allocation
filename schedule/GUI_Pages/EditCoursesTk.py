from __future__ import annotations

from tkinter import *
from typing import Callable, Any, Optional, Protocol

from ..Tk.Scrolled import Scrolled
import schedule.Tk.InitGuiFontsAndColours as fac
from schedule.Tk.AdvancedTreeview import AdvancedTreeview
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
        if self.Fonts is None:
            self.Fonts = fac.TkFonts(frame.winfo_toplevel())
        print(f"Fonts are {self.Fonts}")

        self.resource_Listbox: dict[ResourceType, Listbox] = dict()
        self._frame: Frame = frame
        self._toggle = None
        self._dropped = None

        self.resource_objects: dict[ResourceType, list[Any]] = dict()
        for resource_type in ResourceType:
            self.resource_objects[resource_type] = list()

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
        tree_scrolled: Scrolled = Scrolled(left_panel, 'AdvancedTreeview', scrollbars='se')
        tree_scrolled.pack(expand=1, fill='both', side='left')
        self.course_ttkTreeView: AdvancedTreeview = tree_scrolled.widget
        self.course_ttkTreeView.bind('<Double-1>', self._cmd_edit_selection)
        self.course_ttkTreeView.bind('<Key-Return>', self._cmd_edit_selection)
        self.course_ttkTreeView.tag_configure("bold", font=self.Fonts.bold)
        self.course_ttkTreeView.tag_configure("normal", font=self.Fonts.normal)

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
    def update_resource_type_objects(self, resource_type: ResourceType, objs: list[Any]):
        """
        Updates the Listbox widget with Labs/Teachers/Streams string representations
        :param resource_type: what view resource_type are you updating?
        :param objs: all the objects that you want in the list
        """
        widget: Listbox = self.resource_Listbox[resource_type]
        print(f"{widget=}")
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
        Label(f, text="Teachers",font=self.Fonts.bold).pack()
        sf = Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='e')
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

        # self.view_type_tk_lists[ResourceType.teacher].bind('<Double-Button-1>', self._cmd_double_click_teacher)
        #
        # # ---------------------------------------------------------------
        # # unbind the motion for general listbox widgets, which interferes
        # # with the drag-drop bindings later on.
        # # ---------------------------------------------------------------
        # for resource_type in ResourceType:
        #     self.view_type_tk_lists[resource_type].bind('<B1-Motion>', None)
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
