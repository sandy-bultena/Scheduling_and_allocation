from tkinter import *
from tkinter import ttk
from ..Tk.scrolled import Scrolled
from ..PerlLib.Colours import Colour
from tkinter.font import Font
from ..GUI.FontsAndColoursTk import FontsAndColoursTk
import re


# =================================================================
# Edit courses GUI
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
#   cb_get_scheduable_menu_info     (teacher_lab_stream_id, type)
#   cb_get_tree_menu                (selected_object, parent_object, tree_path)
#   cb_new_course                   ()
#   cb_show_teacher_stat            (teacher_id)
# =================================================================

class EditCoursesTk:
    Colours: dict[str, str] = FontsAndColoursTk.colours
    Fonts: dict[str, Font] = FontsAndColoursTk.font
    Text_style_defn: dict[str, str] = {'bg': Colours["DarkBackground"], 'fg': Colours["SelectedForeground"]}

    def __init__(self, frame: Frame):
        self.__tk_frame: Frame = frame
        self.__tk_labs_list = None
        self.__tk_streams_list = None
        self.__tk_teachers_list = None

        self.__toggle = None
        self.__dropped = None

        self.__tree_objs: dict[str:object] = dict()
        self.cb_edit_obj: callable[object,str] = lambda obj, obj_id: None
        self.cb_new_course: callable = lambda : None
        self.cb_get_tree_menu: callable[object,str] = lambda obj, obj_id: list()

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
        left_panel.grid(row=0, clumn=0, sticky='nsew')

        # calculate min_width of left panel based on screen size
        width, _, _ = re.match(r"^=?(\d+)x(\d+)?([+-]\d+[+-]\d+)?$", frame.winfo_toplevel().geometry()).groups()
        min_width = int(7 / 16 * width)

        # relative weights etc to widths
        frame.grid_columnconfigure(0, minsize=min_width, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------------------
        # make Schedule tree
        # ----------------------------------------------------------------
        tree_scrolled: Scrolled = Scrolled(left_panel, 'Treeview', scrollbars='se')
        tree_scrolled.pack(expand=1, fill='both', side='left')
        self.__tree: ttk.Treeview = tree_scrolled.widget
        self.__tree.bind('<Double-1>', self.__cmd_edit_selection)
        self.__tree.bind('<Key-Return>', self.__cmd_edit_selection)

        # ----------------------------------------------------------------
        # make panel for modifying Schedule
        # ----------------------------------------------------------------
        panel = Frame(right_panel)
        panel.pack(expand=1, fill='both', side='right')
        self.__create_panel_for_modifying(panel)

        # -------------------------------
        # Right click menu binding
        # -------------------------------
        self.__create_right_click_menu(tree_scrolled)

        # ----------------------------------------------------------------
        # drag and drop bindings
        # ----------------------------------------------------------------
        self.__create_drag_drop_objs()

    # ===================================================================
    # create panel for modifying the schedule
    # ===================================================================
    def __create_panel_for_modifying(self, panel):

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

        btn_edit_selection = Button(button_row, text="Edit Selection", width=11, command=self.__cmd_edit_selection)
        btn_edit_selection.pack(side='left')

        # ---------------------------------------------------------------
        # teacher and lab and stream list
        # ---------------------------------------------------------------
        teachers_scrolled_list = Scrolled(panel, 'Listbox', scrollbars='e')
        teachers_scrolled_list.grid(column=0, stick='nsew', row=0)

        labs_scrolled_list = Scrolled(panel, 'Listbox', scrollbars='e')
        labs_scrolled_list.grid(column=0, sticky='nsew', row=1)

        streams_scrolled_list = Scrolled(panel, 'Listbox', scrollbars='e')
        streams_scrolled_list.grid(column=0, sticky='nsew', row=2)

        self.__tk_labs_list = teachers_scrolled_list.widget
        self.__tk_streams_list = labs_scrolled_list.widget
        self.__tk_teachers_list = streams_scrolled_list.widget

        # ---------------------------------------------------------------
        # unbind the motion for general listbox widgets, which interferes
        # with the drag-drop bindings later on.
        # ---------------------------------------------------------------
        self.__tk_teachers_list.bind('<B1-Motion>', None)
        self.__tk_teachers_list.bind('<Double-Button-1>', self.__cmd_double_click_teacher)

        # ---------------------------------------------------------------
        # assign weights to the panel grid
        # ---------------------------------------------------------------
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=2)
        panel.grid_rowconfigure(2, weight=2)
        panel.grid_rowconfigure(3, weight=0)

    # ==================================================================
    # create all the right click menu stuff
    # ==================================================================
    def __create_right_click_menu(self, scrolled_tree):
        lab_menu = Menu(self.__tk_labs_list, tearoff=0)
        stream_menu = Menu(self.__tk_streams_list, tearoff=0)
        self.__tk_teachers_list.bind('<Button-2>',
                                     lambda e: self.__cmd_show_schedulable_menu('teacher', e))
        self.__tk_labs_list.bind('<Button-2>',
                                 lambda e: self.__cmd_show_schedulable_menu('lab', e))
        self.__tk_streams_list.bind('<Button-2>',
                                    lambda e: self.__cmd_show_schedulable_menu('stream', e))
        self.__tree.bind('<Button-2>', self.__cmd_show_tree_menu)

    # ==================================================================
    # show pop-up tree menu
    # ==================================================================
    def __cmd_show_tree_menu(self, e: Event):
        tree: ttk.Treeview = self.__tree

        # which entity was selected (based on mouse position), and set focus and selection
        entity_id = tree.identify_row(e.y)
        if not entity_id:
            return
        tree.selection_clear()
        tree.selection_set(entity_id)
        tree.focus(entity_id)

        # get the object and parent object associated with the selected item,
        # if no parent (i.e. Schedule) we don't need a drop down menu
        parent = self.__get_parent(entity_id)
        if not parent:
            return

        # create the drop down menu
        menu_array: list[str] = self.cb_get_tree_menu(self.__tree_objs[entity_id])
        tree_menu = Menu(self.__tree, tearoff=0, menuitems=menu_array)
        '''
    my $menu_array = $self->cb_get_tree_menu->( $obj, $parent_obj, $path );
    my $tree_menu = $tree->Menu( -tearoff => 0, -menuitems => $menu_array );
    $tree_menu->post( $x, $y );
}
'''

    def __cmd_show_schedulable_menu(self, menu_type: str, e: Event):
        pass

    def __cmd_double_click_teacher(self, teachers_list: list[object], e: Event):
        pass

    # =================================================================
    # get the parents of a particular object
    # =================================================================
    def get_parents(self, tree_item_id: str) -> list[object]:
        return list(self.__get_parent(self.__tree.parent(tree_item_id)))

    def __get_parent(self, tree_item_id: str):
        while tree_item_id != "":
            yield tree_item_id
            tree_item_id = self.__tree.parent(tree_item_id)

    # =================================================================
    # Callback functions
    # =================================================================
    def __cmd_edit_selection(self, *args) -> None:
        tree_item_id = self.__tree.focus()
        obj = self.__tree_objs[tree_item_id]
        self.cb_edit_obj(obj, tree_item_id)

    # =================================================================
    # create all the drag'n'drop stuff
    # =================================================================
    def __create_drag_drop_objs(self):

        # -------------------------------------------------------------
        # drag from teachers/labs to course tree
        # -------------------------------------------------------------
        pass


'''
        # -------------------------------------------------------------
        # drag from teachers/labs to course tree
        # -------------------------------------------------------------
        $self->_tk_teachers_list->DragDrop(
            -event        => '<B1-Motion>',
            -sitetypes    => [qw/Local/],
            -startcommand => [
                \&_teacher_lab_start_drag, $self->_tk_teachers_list, 'teacher'
            ],
        );

        $self->_tk_labs_list->DragDrop(
            -event     => '<B1-Motion>',
            -sitetypes => [qw/Local/],
            -startcommand =>
              [ \&_teacher_lab_start_drag, $self->_tk_labs_list, 'lab' ],
        );

        $self->_tk_streams_list->DragDrop(
            -event     => '<B1-Motion>',
            -sitetypes => [qw/Local/],
            -startcommand =>
              [ \&_teacher_lab_start_drag, $self->_tk_streams_list, 'stream' ],
        );

        $tree->DropSite(
            -droptypes     => [qw/Local/],
            -dropcommand   => [ \&_cmd_dropped_on_tree, $self ],
            -motioncommand => [ \&_cmd_dragging_over_tree, $self ],
        );

        # =================================================================
        # tree starting to drag - change name of drag widget to selected item
        # =================================================================
    }

    # =================================================================
    # teacher/lab starting to drag - change name of drag widget to selected item
    # =================================================================
    sub _teacher_lab_start_drag {
        my ( $lb, $type, $drag ) = @_;
        my ($lb_sel) = $lb->curselection;
        my ($req)    = $lb->get($lb_sel);
        $drag->configure(
            -text => $req,
            -font => [qw/-family arial -size 18/],
            -bg   => '#abcdef'
        );
        $Drag_source  = $drag;
        $Dragged_from = $type;
        undef;
    }

}

'''

'''


__setup();

# =================================================================
# Class/Global Variables
# =================================================================
my $Drag_source;
my $Dragged_from;
my $Fonts;
my $Colours;
my %Styles;

# =================================================================
# Constructor
# =================================================================
sub new {
    my $class = shift;
    my $frame = shift;
    $Colours = FontsAndColoursTk->Colours;
    $Fonts   = FontsAndColoursTk->Fonts;

    my $self = bless {}, $class;
    $self->_tk_frame($frame);

    # ----------------------------------------------------------------
    # set up photos and styles, etc.
    # ----------------------------------------------------------------
    $Styles{-course} = $frame->ItemStyle(
        'text',
        -bg => $Colours->{DarkBackground},
        -fg => $Colours->{SelectedForeground},
    );

    # ----------------------------------------------------------------
    # using grid, create right and left panels
    # ----------------------------------------------------------------
    # always start from scratch (- means we are always up to date)
    foreach my $sl ( $frame->gridSlaves ) {
        $sl->destroy;
    }
    my $right_panel =
      $frame->Frame()->grid( -row => 0, -column => 1, -sticky => 'nsew' );
    my $left_panel =
      $frame->Frame()->grid( -row => 0, -column => 0, -sticky => 'nsew' );

    # calculate min_width of left panel based on screen size
    my @x =
      ( $frame->toplevel->geometry() =~ /^=?(\d+)x(\d+)?([+-]\d+[+-]\d+)?$/ );
    my $min_width = 7 / 16 * $x[0];

    # relative weights etc to widths
    $frame->gridColumnconfigure( 0, -minsize => $min_width, -weight => 1 );
    $frame->gridColumnconfigure( 1, -weight => 1 );
    $frame->gridRowconfigure( 0, -weight => 1 );

    # ----------------------------------------------------------------
    # make Schedule tree
    # ----------------------------------------------------------------
    my $tree;
    my $treescrolled = $left_panel->Scrolled(
        'DynamicTree',
        -scrollbars => 'osoe',
        -separator  => '/',
        -command    => [ \&_cmd_edit_selection, $self ],
    )->pack( -expand => 1, -fill => 'both', -side => 'left' );
    $tree = $treescrolled->Subwidget('dynamictree');
    $tree->bind( '<Key-Return>', [ \&_cmd_return, $self ] );
    $self->_tk_tree($tree);

    # ----------------------------------------------------------------
    # make panel for modifying Schedule
    # ----------------------------------------------------------------
    my $panel =
      $right_panel->Frame()
      ->pack( -expand => 1, -fill => 'both', -side => 'right' );

    $self->_create_panel_for_modifying( $tree, $panel );

    #-------------------------------
    # Right click menu binding
    #-------------------------------
    $self->_create_right_click_menu( $treescrolled, $tree );

    # ----------------------------------------------------------------
    # drag and drop bindings
    # ----------------------------------------------------------------
    $self->_create_drag_drop_objs($tree);

    return $self;
}

# =================================================================
# alert the user
# =================================================================
sub alert {
    my $self = shift;
    $self->_tk_tree->bell;
}

# =================================================================
# add node to tree
# =================================================================
sub add {
    my $self    = shift;
    my $path    = shift;
    my %options = @_;
    $self->_tk_tree->add( $path, %options );
    $self->_tk_tree->autosetmode();

}

# =================================================================
# text style for course for the tree
# =================================================================
sub course_style {
    return $Styles{-course};
}

# =================================================================
# delete node from tree
# =================================================================
sub delete {
    my $self           = shift;
    my $type_of_delete = shift;
    my $path           = shift;
    $self->_tk_tree->delete( $type_of_delete, $path )
      if $self->_tk_tree->infoExists($path);
}

# =================================================================
# set labs (put in listbox)
# =================================================================
sub set_labs {
    my $self         = shift;
    my $ids_and_labs = shift;
    $self->_tk_labs_list->delete( 0, 'end' );
    foreach my $lab (@$ids_and_labs) {
        $self->_tk_labs_list->insert( 'end',
            $lab->{-id} . " : " . $lab->{-name} );
    }
}

# =================================================================
# set streams (put in listbox)
# =================================================================
sub set_streams {
    my $self            = shift;
    my $ids_and_streams = shift;
    $self->_tk_streams_list->delete( 0, 'end' );
    foreach my $stream (@$ids_and_streams) {
        $self->_tk_streams_list->insert( 'end',
            $stream->{-id} . " : " . $stream->{-name} );
    }
}

# =================================================================
# set teachers (put in listbox)
# =================================================================
sub set_teachers {
    my $self             = shift;
    my $ids_and_teachers = shift;
    $self->_tk_teachers_list->delete( 0, 'end' );
    foreach my $teacher (@$ids_and_teachers) {
        $self->_tk_teachers_list->insert( 'end',
            $teacher->{-id} . " : " . $teacher->{-name} );
    }
}

# =================================================================
# show message
# =================================================================
sub show_message {
    my $self  = shift;
    my $title = shift;
    my $msg   = shift;

    $self->_tk_frame->messageBox(
        -title   => $title,
        -message => $msg,
        -type    => 'Ok'
    );
}

# =================================================================
# update the text of a particular node in the tree
# =================================================================
sub update_tree_text {
    my $self     = shift;
    my $path     = shift;
    my $new_text = shift;
    my $tree     = $self->_tk_tree;
    return unless $tree->infoExists($path);
    $tree->itemConfigure( $path, 0, -text => $new_text );
}

###################################################################
# Event handlers
###################################################################

# =================================================================
# dropped teacher or lab on tree
# =================================================================
sub _cmd_dropped_on_tree {
    my $self = shift;

    # validate that we have data to work with
    return unless $Dragged_from;
    my ( $obj, $path ) = $self->__selected_obj;
    return unless $path;

    # -------------------------------------------------------------
    # Initialize some variables
    # -------------------------------------------------------------
    my $txt = $Drag_source->cget( -text );
    my $id;
    if ( $txt =~ /^\s*(\d+)\s*:/ ) {
        $id = $1;
    }
    else { return; }

    # -------------------------------------------------------------
    # add appropriate object to object
    # -------------------------------------------------------------
    $self->cb_object_dropped_on_tree->( $Dragged_from, $id, $path, $obj );

    # -------------------------------------------------------------
    # tidy up
    # -------------------------------------------------------------
    $self->_tk_tree->autosetmode();
    $Dragged_from = '';

}


# =================================================================
# teachers_list: <Double-Button-1>
# =================================================================
sub _cmd_double_click_teacher {
    my ( $lb, $self ) = @_;
    my $lb_sel = $lb->curselection;
    my $txt    = $lb->get($lb_sel);

    my $id;
    if ( $txt =~ /^\s*(\d+)\s*:/ ) {
        $id = $1;
    }
    else { return; }
    $self->cb_show_teacher_stat->($id);
}

# ==================================================================
# create and show teacher/lab/stream menu
# ==================================================================
sub _cmd_show_scheduable_menu {
    my ( $list, $type, $self, $x, $y ) = @_;
    my $ent = $list->nearest( $y - $list->rooty );
    $list->selectionClear( 0, 'end' );
    $list->selectionSet($ent) if defined $ent;

    # get id of currently selected scheduable
    my $indices = $list->curselection();
    return unless $indices;
    my $index = $indices->[0] if ref($indices);
    my $scheduable = $list->get($index);
    my $scheduable_id;
    if ( $scheduable =~ /^\s*(\d+)\s*:/ ) {
        $scheduable_id = $1;
    }
    else { return; }

    # get info from Presenter
    my $menu_array =
      $self->cb_get_scheduable_menu_info->( $scheduable_id, $type );

    # create menu
    my $list_menu = $list->Menu( -tearoff => 0, -menuitems => $menu_array );
    $list_menu->post( $x, $y );
}

# ==================================================================
# show pop-up tree menu
# ==================================================================
sub _cmd_show_tree_menu {
    my $tree = shift;
    my $self = shift;
    my ( $x, $y ) = @_;

    my $ent = $tree->nearest( $y - $tree->rooty );
    $tree->selectionClear;
    $tree->anchorClear;
    $tree->selectionSet($ent) if $ent;

    # what was selected? If nothing, bail out
    my ( $obj, $path ) = $self->__selected_obj();
    return unless $path;

    # get the object and parent object associated with the selected item,
    # if no parent (i.e. Schedule) we don't need a drop down menu
    my $parent = $tree->info( 'parent', $path );
    return unless $parent;
    my $parent_obj = $tree->infoData($parent)->{-obj};

    # create the drop down menu
    my $menu_array = $self->cb_get_tree_menu->( $obj, $parent_obj, $path );
    my $tree_menu = $tree->Menu( -tearoff => 0, -menuitems => $menu_array );
    $tree_menu->post( $x, $y );
}

# =================================================================
# trying to drop a lab/teacher onto the tree
# =================================================================
sub _cmd_dragging_over_tree {
    my $self = shift;
    my $tree = $self->_tk_tree;
    my $x    = shift;
    my $y    = shift;

    # ignore this if trying to drop from tree to tree
    return if $Dragged_from eq 'Tree';

    # get the nearest item, and if it is good to
    # drop on it, set the selection

    my $ent = $tree->GetNearest($y);
    $tree->selectionClear;
    $tree->anchorClear;

    if ($ent) {

        ###### TODO ... no isa!
        my $obj = $tree->infoData($ent)->{-obj};
        if ( $obj->isa('Block') || $obj->isa('Section') || $obj->isa('Course') )
        {
            $tree->selectionSet($ent);
        }
    }
}


# ===================================================================
# create panel for modifying the schedule
# ===================================================================
sub _create_panel_for_modifying {
    my $self = shift;

    my $tree  = shift;
    my $panel = shift;

    # ---------------------------------------------------------------
    # button row
    # ---------------------------------------------------------------
    my $button_row = $panel->Frame->grid(
        -column => 0,
        -sticky => 'nwes',
        -row    => 3
    );

    # ---------------------------------------------------------------
    # buttons
    # ---------------------------------------------------------------
    $button_row->Button(
        -text    => "New Course",
        -width   => 11,
        -command => sub{$self->cb_new_course->()},
    )->pack( -side => 'left' );

    $button_row->Button(
        -text    => "Edit Selection",
        -width   => 11,
        -command => [ \&_cmd_edit_selection, $self ]
    )->pack( -side => 'left' );

    # ---------------------------------------------------------------
    # teacher and lab and stream list
    # ---------------------------------------------------------------
    my $teachers_list =
      $panel->Scrolled( 'Listbox', -scrollbars => 'oe' )
      ->grid( -column => 0, -sticky => 'nwes', -row => 0 );

    my $labs_list =
      $panel->Scrolled( 'Listbox', -scrollbars => 'oe' )
      ->grid( -column => 0, -sticky => 'nwes', -row => 1 );

    my $streams_list =
      $panel->Scrolled( 'Listbox', -scrollbars => 'oe' )
      ->grid( -column => 0, -sticky => 'nwes', -row => 2 );

    $teachers_list = $teachers_list->Subwidget('listbox');
    $labs_list     = $labs_list->Subwidget('listbox');
    $streams_list  = $streams_list->Subwidget('listbox');

    # ---------------------------------------------------------------
    # unbind the motion for general listbox widgets, which interferes
    # with the drag-drop bindings later on.
    # ---------------------------------------------------------------
    $teachers_list->bind( '<B1-Motion>', undef );
    $teachers_list->bind( "<Double-Button-1>",
        [ \&_cmd_double_click_teacher, $teachers_list, $self ] );

    # ---------------------------------------------------------------
    # assign weights to the panel grid
    # ---------------------------------------------------------------
    $panel->gridColumnconfigure( 0, -weight => 1 );
    $panel->gridRowconfigure( 0, -weight => 1 );
    $panel->gridRowconfigure( 1, -weight => 2 );
    $panel->gridRowconfigure( 2, -weight => 2 );
    $panel->gridRowconfigure( 3, -weight => 0 );

    $self->_tk_labs_list($labs_list);
    $self->_tk_streams_list($streams_list);
    $self->_tk_teachers_list($teachers_list);

}


# =================================================================
# create all the drag'n'drop stuff
# =================================================================
{
    my $toggle;
    my $dropped;

    sub _create_drag_drop_objs {
        my $self = shift;
        my $tree = shift;

        # -------------------------------------------------------------
        # drag from teachers/labs to course tree
        # -------------------------------------------------------------
        $self->_tk_teachers_list->DragDrop(
            -event        => '<B1-Motion>',
            -sitetypes    => [qw/Local/],
            -startcommand => [
                \&_teacher_lab_start_drag, $self->_tk_teachers_list, 'teacher'
            ],
        );

        $self->_tk_labs_list->DragDrop(
            -event     => '<B1-Motion>',
            -sitetypes => [qw/Local/],
            -startcommand =>
              [ \&_teacher_lab_start_drag, $self->_tk_labs_list, 'lab' ],
        );

        $self->_tk_streams_list->DragDrop(
            -event     => '<B1-Motion>',
            -sitetypes => [qw/Local/],
            -startcommand =>
              [ \&_teacher_lab_start_drag, $self->_tk_streams_list, 'stream' ],
        );

        $tree->DropSite(
            -droptypes     => [qw/Local/],
            -dropcommand   => [ \&_cmd_dropped_on_tree, $self ],
            -motioncommand => [ \&_cmd_dragging_over_tree, $self ],
        );

        # =================================================================
        # tree starting to drag - change name of drag widget to selected item
        # =================================================================
    }

    # =================================================================
    # teacher/lab starting to drag - change name of drag widget to selected item
    # =================================================================
    sub _teacher_lab_start_drag {
        my ( $lb, $type, $drag ) = @_;
        my ($lb_sel) = $lb->curselection;
        my ($req)    = $lb->get($lb_sel);
        $drag->configure(
            -text => $req,
            -font => [qw/-family arial -size 18/],
            -bg   => '#abcdef'
        );
        $Drag_source  = $drag;
        $Dragged_from = $type;
        undef;
    }

}


# =================================================================
# get the object from the specified tree path
# =================================================================
sub __get_obj {
    my $self = shift;
    my $path = shift;

    my $obj;
    if ($path) {
        $path = ( ref $path ) ? $path->[0] : $path;
        $obj = $self->_tk_tree->infoData($path)->{-obj};
    }

    return $obj;
}

sub __setup {

    # ------------------------------------------------------------------------
    # Entry or Text Box variable bindings
    # ------------------------------------------------------------------------
    __create_setters_and_getters(
        -category   => 'list',
        -properties => [qw()],
        -default    => {}
    );

    __create_setters_and_getters(
        -category   => "_tb",
        -properties => [qw( )],
        -default    => ""
    );

    __create_setters_and_getters(
        -category   => "_new",
        -properties => [qw()],
        -default    => ""
    );

    # ------------------------------------------------------------------------
    # getters and setters for callback routines
    # ------------------------------------------------------------------------
    my @callbacks = (
        qw(object_dropped_on_tree edit_obj show_teacher_stat new_course
          get_scheduable_menu_info get_tree_menu)
    );

    __create_setters_and_getters(
        -category   => "cb",
        -properties => \@callbacks,
        -default    => sub { print "not implemented\n", caller(), "\n"; return }
    );

    # ------------------------------------------------------------------------
    # Defining widget getters and setters
    # ------------------------------------------------------------------------
    my @widgets = (qw(labs_list teachers_list streams_list tree frame));
    __create_setters_and_getters(
        -category   => "_tk",
        -properties => \@widgets,
        -default    => undef
    );

}

# ============================================================================
# getters and setters
# - creates two subs for each property
# 1) cat_property
# 2) cat_property_ptr
# ============================================================================
sub __create_setters_and_getters {

    my %stuff   = @_;
    my $cat     = $stuff{-category};
    my $props   = $stuff{-properties};
    my $default = $stuff{-default};

    foreach my $prop (@$props) {
        no strict 'refs';

        # create simple getter and setter
        *{ $cat . "_" . $prop } = sub {
            my $self = shift;
            $self->{ $cat . "_" . $prop } = shift if @_;
            return $self->{ $cat . "_" . $prop } || $default;
        };

        # set getter to property pointer
        *{ $cat . "_" . $prop . "_ptr" } = sub {
            my $self = shift;
            return \$self->{ $cat . "_" . $prop };
          }
    }
}

1;
'''
