#!/usr/bin/perl
use strict;
use warnings;

package EditCoursesTk;
use FindBin;
use Carp;
use Tk;
use lib "$FindBin::Bin/..";

#use GuiSchedule::EditCoursesDialogs;
use Tk::DynamicTree;
use Tk::DragDrop;
use Tk::DropSite;
use Tk::ItemStyle;
use PerlLib::Colours;
use Tk::FindImages;
use Tk::Dialog;
use Tk::LabEntry;
use Tk::Optionmenu;
use Tk::Menu;
use GUI::FontsAndColoursTk;

__setup();

# =================================================================
# Class/Global Variables
# =================================================================
my $Drag_source;
my $Dragged_from;
my $Fonts;
my $Colours;
my %Styles;

sub new {
    my $class = shift;
    my $frame = shift;
    $Colours = FontsAndColoursTk->Colours;
    $Fonts = FontsAndColoursTk->Fonts;

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
        -command    => [ \&_edit_selection, $self ],
    )->pack( -expand => 1, -fill => 'both', -side => 'left' );
    $tree = $treescrolled->Subwidget('dynamictree');
    $tree->bind( '<Key-Return>', [ \&_return, $self ] );
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

###################################################################
# Event handlers
###################################################################

# =================================================================
# tree: <Key-Return>
# =================================================================
sub _return {
    my $self = shift;
    #### TODO: is this correct?
    return if $self->_tk_tree->infoAnchor;
    my $path = $self->_tk_tree->selectionGet();
    $self->_edit_selection($path) if $path;
}

# =================================================================
# tree: <command>, Edit Selection button: <command>
# =================================================================
sub _edit_selection {
    my $self = shift;
    my $path = shift;
    my $obj  = $self->_get_obj($path);
    $self->cb_edit_obj->( $obj, $path );
}

# =================================================================
# teachers_list: <Double-Button-1>
# =================================================================
sub _double_click_teacher {
    my ( $lb, $self ) = @_;
    my $lb_sel  = $lb->curselection;
    my $teachID = $lb->get($lb_sel);

    ( my $id ) = split " ", $teachID;
    chop $id;

    $self->cb_show_teacher_stat->($id);
}

# =================================================================
# New Course Button: <command> => $self->cb_new_course
# =================================================================

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
        -command => $self->cb_new_course,
    )->pack( -side => 'left' );

    $button_row->Button(
        -text    => "Edit Selection",
        -width   => 11,
        -command => [ \&_edit_selection, $self ]
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
        [ \&_double_click_teacher, $teachers_list, $self ] );

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
    print $self->_tk_teachers_list,"\n";

}

#==================================================================
#create all the right click menu stuff
#==================================================================
sub _create_right_click_menu {
    my $self         = shift;
    my $treescrolled = shift;
    my $tree         = shift;

    my $lab_menu = $self->_tk_labs_list->Menu( -tearoff => 0 );
    my $stream_menu = $self->_tk_streams_list->Menu( -tearoff => 0 );

    $self->_tk_teachers_list->bind( '<Button-3>',
        [ \&_show_scheduable_menu, 'teacher', $self, Ev('X'), Ev('Y') ] );

    $self->_tk_labs_list->bind( '<Button-3>',
        [ \&_show_scheduable_menu, 'lab', $self, Ev('X'), Ev('Y') ] );

    $self->_tk_streams_list->bind( '<Button-3>',
        [ \&_show_scheduable_menu, $self, Ev('X'), Ev('Y') ] );

    $tree->bind( '<Button-3>', [ \&_show_tree_menu, $self, Ev('X'), Ev('Y') ] );

}

# ==================================================================
# create and show teacher/lab/stream menu
# ==================================================================
sub _show_scheduable_menu {
    my ( $list, $type, $self, $x, $y ) = @_;

    # get id of currently selected scheduable
    my @indices = $list->curselection();
    return unless @indices;

    my $scheduable = $list->get( $indices[0] );
    ( my $scheduable_id ) = split " ", $scheduable;
    chop $scheduable_id;

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
sub _show_tree_menu {
    my $tree = shift;
    my $self = shift;
    my ( $x, $y ) = @_;

    # what was selected? If nothing, bail out
    my ($path, $obj) = $self->_selected_obj();
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

        $self->_tk_teachers_list->DropSite(
            -droptypes   => [qw/Local/],
            -dropcommand => [ \&_drop_on_trash, $self ],
        );

        $self->_tk_labs_list->DragDrop(
            -event     => '<B1-Motion>',
            -sitetypes => [qw/Local/],
            -startcommand =>
              [ \&_teacher_lab_start_drag, $self->_tk_labs_list, 'lab' ],
        );

        $self->_tk_labs_list->DropSite(
            -droptypes   => [qw/Local/],
            -dropcommand => [ \&_drop_on_trash, $self ],
        );

        $self->_tk_streams_list->DragDrop(
            -event     => '<B1-Motion>',
            -sitetypes => [qw/Local/],
            -startcommand =>
              [ \&_teacher_lab_start_drag, $self->_tk_streams_list, 'stream' ],
        );

        $self->_tk_streams_list->DropSite(
            -droptypes   => [qw/Local/],
            -dropcommand => [ \&_drop_on_trash, $self ],
        );

        $tree->DropSite(
            -droptypes     => [qw/Local/],
            -dropcommand   => [ \&_dropped_on_tree, $self ],
            -motioncommand => [ \&_dragging_over_tree, $self ],
        );

        # -------------------------------------------------------------
        # drag from course tree to trash can
        # -------------------------------------------------------------
        $tree->DragDrop(
            -event        => '<B1-Motion>',
            -sitetypes    => [qw/Local/],
            -startcommand => [ \&_course_tree_start_start_drag, $self ],
        );

        # =================================================================
        # tree starting to drag - change name of drag widget to selected item
        # =================================================================
        sub _course_tree_start_start_drag {
            my ( $self, $trash_label, $drag ) = @_;
            $trash_label->configure(
                -bg => $Colours->{WorkspaceColour},
                -fg => $Colours->{WindowForeground},
            );

            my $path = $self->_tk_tree->selectionGet();

            $Drag_source  = $drag;
            $Dragged_from = 'Tree';
            $dropped      = 0;
            $toggle       = 0;

            return unless $path;

            $drag->configure(
                -text => $self->_tk_tree->itemCget( $path, 0, -text ),
                -font => [qw/-family arial -size 18/],
                -bg   => '#abcdef'
            );

            undef;
        }
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

    # =================================================================
    # dropped item on trash can
    # =================================================================
    sub _drop_on_trash {

        my $self = shift;
        my $tree = shift;

        # validate that we have data to work with
        return unless $Dragged_from;
        my ( $obj, $path ) = $self->_selected_obj;
        return unless $path;

        # get parent widget
        my $parent_path = $tree->info( 'parent', $path );
        return unless $parent_path;
        my $parent_obj = $tree->infoData($parent_path)->{-obj};

        # remove object
        $tree->delete( 'offsprings', $parent_path );
        $tree->update;
        $self->cb_trash->( $parent_obj, $obj, $parent_path );
        $tree->autosetmode();

        # -------------------------------------------------------------
        # tidy up
        # -------------------------------------------------------------
        $tree->autosetmode();
        $Dragged_from = '';
    }
}

# =================================================================
# get object that is currently selected item on tree
# =================================================================
sub _selected_obj {
    my $self = shift;
    my $tree = $self->_tk_tree;

    my $path = $tree->selectionGet();
    return ( undef, $path ) unless $path;

    # get info about dropped object
    $path = ( ref $path ) ? $path->[0] : $path;
    my $obj = $tree->infoData($path)->{-obj};

    return ( $obj, $path );
}

# =================================================================
# get the object from the specified tree path
# =================================================================
sub _get_obj {
    my $self = shift;
    my $path = shift;

    my $obj;
    if ($path) {
        $path = ( ref $path ) ? $path->[0] : $path;
        $obj = $self->_tk_tree->infoData($path)->{-obj};
    }

    return $obj;
}

# =================================================================
# dropped teacher or lab on tree
# =================================================================
sub _dropped_on_tree {
    my $self = shift;

    # validate that we have data to work with
    return unless $Dragged_from;
    my ( $obj, $path ) = $self->selected_obj;
    return unless $path;

    # -------------------------------------------------------------
    # Initialize some variables
    # -------------------------------------------------------------
    my $txt = $Drag_source->cget( -text );
    ( my $id ) = split " ", $txt;
    chop $id;

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
# trying to drop a lab/teacher onto the tree
# =================================================================
sub _dragging_over_tree {
    my $self = shift;
    my $tree = shift;
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

############# New ########################

sub set_teachers {
    my $self             = shift;
    my $ids_and_teachers = shift;
    foreach my $teacher (@$ids_and_teachers) {
        $self->_tk_teachers_list->insert( 'end',
            $teacher->{-id} . " : " . $teacher->{-name} );
    }
}

sub set_streams {
    my $self            = shift;
    my $ids_and_streams = shift;
    foreach my $stream (@$ids_and_streams) {
        $self->_tk_streams_list->insert( 'end',
            $stream->{-id} . " : " . $stream->{-name} );
    }
}

sub set_labs {
    my $self         = shift;
    my $ids_and_labs = shift;
    foreach my $lab (@$ids_and_labs) {
        $self->_tk_labs_list->insert( 'end',
            $lab->{-id} . " : " . $lab->{-name} );
    }
}

sub add {
    my $self    = shift;
    my $path    = shift;
    my %options = @_;
    $self->_tk_tree->add( $path, %options );
    $self->_tk_tree->autosetmode();

}

sub delete {
    my $self           = shift;
    my $type_of_delete = shift;
    my $path           = shift;
    $self->_tk_tree->delete( $type_of_delete, $path );
}

sub course_style {
    return $Styles{-course};
}

sub alert {
    my $self = shift;
    $self->_tk_tree->bell;
}

sub message_box {
    my $self  = shift;
    my $title = shift;
    my $msg   = shift;

    $self->_tk_frame( -title => $title, -message => $msg, -type => 'Ok' );
}

sub __setup {

    # ------------------------------------------------------------------------
    # Entry or Text Box variable bindings
    # ------------------------------------------------------------------------
    _create_setters_and_getters(
        -category   => 'list',
        -properties => [qw()],
        -default    => {}
    );

    _create_setters_and_getters(
        -category   => "_tb",
        -properties => [qw( )],
        -default    => ""
    );

    _create_setters_and_getters(
        -category   => "_new",
        -properties => [qw()],
        -default    => ""
    );

    # ------------------------------------------------------------------------
    # getters and setters for callback routines
    # ------------------------------------------------------------------------
    my @callbacks = (
        qw(trash object_dropped_on_tree edit_obj show_teacher_stat
          new_course get_scheduable_menu_info set_teacher_to_blocks
          set_teacher_to_sections set_lab_to_blocks set_lab_to_sections
          set_stream_to_sections cb_get_tree_menu)
    );
    _create_setters_and_getters(
        -category   => "cb",
        -properties => \@callbacks,
        -default    => sub { return }
    );

    # ------------------------------------------------------------------------
    # Tk Labels
    # ------------------------------------------------------------------------
    my @labels = (
        qw (
          )
    );
    _create_setters_and_getters(
        -category   => "_lbl",
        -properties => \@labels,
        -default    => undef
    );

    # ------------------------------------------------------------------------
    # Defining widget getters and setters
    # ------------------------------------------------------------------------
    my @widgets = (
        qw(labs_list teachers_list streams_list tree frame

          )
    );
    _create_setters_and_getters(
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
sub _create_setters_and_getters {

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
