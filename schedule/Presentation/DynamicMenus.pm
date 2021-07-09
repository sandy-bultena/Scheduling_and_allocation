#!/usr/bin/perl
use strict;
use warnings;

package DynamicMenus;

my $Schedule;
my $Parent_presenter;

# ============================================================================
# create popup menus for trees
# - menus are dynamic, depending on the current schedule, and what
#   tree item was selected
# ============================================================================
sub create_tree_menus {
    $Schedule = shift;
    my $sel_obj   = shift;    # selected object
    my $par_obj   = shift;    # parent object
    my $tree_path = shift;    # tree path (i.e. parent.child)

    my $type = $Schedule->get_object_type($sel_obj);
    my $menu = [];

    # ------------------------------------------------------------------------
    # course
    # ------------------------------------------------------------------------
    if ( $type eq 'course' ) {
        _remove_item( $menu, $sel_obj, $Schedule, $tree_path, "Remove Course" );
        _add_teachers( $menu, $sel_obj, $tree_path );
        _add_section_edit_course( $menu, $sel_obj, $tree_path );
        _needs_allocation( $menu, $sel_obj, $tree_path );
        _remove_teachers( $menu, $sel_obj, $tree_path );
        _remove_all( $menu, $sel_obj, $tree_path );
    }

    # ------------------------------------------------------------------------
    # section
    # ------------------------------------------------------------------------
    elsif ( $type eq 'section' ) {
        _remove_item( $menu, $sel_obj, $par_obj, $tree_path, "Remove Section" );
        _add_teachers( $menu, $sel_obj, $tree_path );
        _add_labs( $menu, $sel_obj, $tree_path );
        _add_streams( $menu, $sel_obj, $tree_path );
        _add_blocks_edit_section( $menu, $sel_obj, $tree_path );
        _remove_blocks( $menu, $sel_obj, $tree_path );
        _remove_teachers( $menu, $sel_obj, $tree_path );
        _remove_labs( $menu, $sel_obj, $tree_path );
        _remove_streams( $menu, $sel_obj, $tree_path );
        _remove_all( $menu, $sel_obj, $tree_path );
    }

    # ------------------------------------------------------------------------
    # block
    # ------------------------------------------------------------------------
    elsif ( $type eq 'block' ) {
        _remove_item( $menu, $sel_obj, $par_obj, $tree_path, "Remove Block" );
        _add_teachers( $menu, $sel_obj, $tree_path );
        _add_labs( $menu, $sel_obj, $tree_path );
        _remove_teachers( $menu, $sel_obj, $tree_path );
        _remove_labs( $menu, $sel_obj, $tree_path );
        _remove_all( $menu, $sel_obj, $tree_path );
    }

    # ------------------------------------------------------------------------
    # lab/teacher
    # ------------------------------------------------------------------------
    elsif ( $type eq 'teacher' ) {
        _remove_item( $menu, $sel_obj, $par_obj, $tree_path, "Remove Teacher" );
    }
    elsif ( $type eq 'lab' ) {
        _remove_item( $menu, $sel_obj, $par_obj, $tree_path, "Remove Lab" );
    }
    return $menu;

}

# ============================================================================
# create popup menus for streams/labs/teacher
# - menus are dynamic, depending on the current schedule, and what
#   type of object was selected
# ============================================================================
sub show_scheduable_menu {
    my $Schedule   = shift;
    my $sel_obj_id = shift;
    my $type       = shift;
    my $sel_obj    = $Schedule->get_object_by_id_and_type( $sel_obj_id, $type );

    my $menu    = [];
    my $courses = [];

    push @$menu,
      [
        'cascade', "Add $type to Course",
        -tearoff   => 0,
        -menuitems => $courses
      ];

    # ------------------------------------------------------------------------
    # all courses
    # ------------------------------------------------------------------------
    foreach my $course ( sort { &_sort_by_alphabet } $Schedule->courses->list )
    {
        my $sections = [];
        push @$courses,
          [
            'cascade', $course->short_description,
            -tearoff   => 0,
            -menuitems => $sections
          ];
        if ( $type ne 'stream' ) {
            push @$sections,
              [
                'command',
                'All Sections',
                -command => [
                    \&EditCourses::assign_obj2_to_obj1,
                    $course,
                    $sel_obj,
                    "Schedule/Course" . $course->id,
                ]
              ];
        }

        # --------------------------------------------------------------------
        # all sections per course
        # --------------------------------------------------------------------
        foreach my $section ( sort { &_sort_by_number } $course->sections ) {
            my $blocks = [];
            push @$sections,
              [ "cascade", "$section", -tearoff => 0, -menuitems => $blocks ];
            push @$blocks,
              [
                'command',
                'All Blocks',
                -command => [
                    \&EditCourses::assign_obj2_to_obj1,
                    $section,
                    $sel_obj,
                    "Schedule/Course" . $course->id . "/Section" . $section->id
                ]
              ];

            # ----------------------------------------------------------------
            # all blocks per section
            # ---------------------------------------------------------------
            if ( $type ne 'stream' ) {
                foreach
                  my $block ( sort { &_sort_by_block_id } $section->blocks )
                {
                    push @$blocks,
                      [
                        'command',
                        "$block",
                        -command => [
                            \&EditCourses::assign_obj2_to_obj1,
                            $block,
                            $sel_obj,
                            "Schedule/Course"
                              . $course->id
                              . "/Section"
                              . $section->id
                              . "/Block"
                              . $block->id
                        ]
                      ];

                }
            }

        }

    }
    return $menu;
}

# --------------------------------------------------------------------
# generic, adding multiple items
# --------------------------------------------------------------------
sub _add_items {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;
    my $items     = shift;
    my $title     = shift;

    my $menu_items = [];
    foreach my $item (@$items) {
        push @$menu_items,
          [
            "command",
            $item->{name},
            -command => [
                \&EditCourses::assign_obj2_to_obj1,
                $sel_obj, $item->{obj}, $tree_path
            ]
          ];
    }
    push @$menu,
      [
        "cascade", $title,
        -tearoff   => 0,
        -menuitems => $menu_items
      ];
}

# --------------------------------------------------------------------
# adding teachers
# --------------------------------------------------------------------
sub _add_teachers {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;
    my $teachers  = [];
    foreach
      my $teacher ( sort { &_sort_by_teacher_name } $Schedule->all_teachers )
    {
        next if $sel_obj->has_teacher($teacher);
        push @$teachers, { name => "$teacher", obj => $teacher };
    }
    _add_items( $menu, $sel_obj, $tree_path, $teachers, "Add Teacher" );
}

# --------------------------------------------------------------------
# adding labs
# --------------------------------------------------------------------
sub _add_labs {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $labs = [];
    foreach my $lab ( $Schedule->all_labs ) {
        next if $sel_obj->has_lab($lab);
        push @$labs, { name => "$lab", obj => $lab };
    }
    _add_items( $menu, $sel_obj, $tree_path, $labs, "Add Lab" );
}

# --------------------------------------------------------------------
# adding streams
# --------------------------------------------------------------------
sub _add_streams {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $streams = [];
    foreach my $stream ( $Schedule->all_streams ) {
        next if $sel_obj->has_stream($stream);
        push @$streams, { name => "$stream", obj => $stream };
    }
    _add_items( $menu, $sel_obj, $tree_path, $streams, "Add Stream" );
}

# --------------------------------------------------------------------
# add blocks, edit section
# --------------------------------------------------------------------
sub _add_blocks_edit_section {
    my $menu    = shift;
    my $sel_obj = shift;
    my $tree_path;

    push @$menu,
      [
        'command',
        "Add Blocks",
        -command => [ \&EditCourse::add_blocks_dialog, $sel_obj, $tree_path ]
      ];
    push @$menu,
      [
        'command',
        "Edit Section",
        -command => [ \&EditCourses::edit_section_dialog, $sel_obj, $tree_path ]
      ];
    push @$menu, "separator";
}

# --------------------------------------------------------------------
# add sections, edit course
# --------------------------------------------------------------------
sub _add_section_edit_course {
    my $menu    = shift;
    my $sel_obj = shift;
    my $tree_path;
    push @$menu,
      [
        'command',
        "Add Sections(s)",
        -command => [ \&EditCourses::add_section_dialog, $sel_obj, $tree_path ]
      ];

    push @$menu,
      [
        'command',
        "Edit Course",
        -command => [ \&EditCourses::edit_course_dialog, $sel_obj, $tree_path ]
      ];
    push @$menu, "separator";
}

# --------------------------------------------------------------------
# needs allocation
# --------------------------------------------------------------------
sub _needs_allocation {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;
    if ( $sel_obj->needs_allocation ) {
        push @$menu, [
            "command",
            "unset 'needs allocation'",
            -command => sub {
                $sel_obj->needs_allocation(0);
                EditCourses::set_dirty();
            },
        ];
    }
    else {
        push @$menu, [
            "command",
            "set 'needs allocation'",
            -command => sub {
                $sel_obj->needs_allocation(1);
                EditCourses::set_dirty();
            },
        ];
    }
    push @$menu, "separator";
}

# --------------------------------------------------------------------
# removing items
# --------------------------------------------------------------------
sub _remove_items {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;
    my $items     = shift;
    my $what      = shift;
    my $type      = shift;

    my $menu_items = [];
    push @$menu_items,
      [
        "command",
        "All $what",
        -command => [
            \&EditCourses::remove_all_type_from_obj1,
            $sel_obj, $type, $tree_path
        ]
      ];
    push @$menu_items, "separator";

    foreach my $item (@$items) {
        push @$menu_items,
          [
            "command",
            $item->{name},
            -command => [
                \&EditCourses::remove_obj2_from_obj1,
                $sel_obj, $item->{obj}, $tree_path
            ]
          ];
    }
    push @$menu,
      [
        "cascade", "Remove $what",
        -tearoff   => 0,
        -menuitems => $menu_items
      ];
}

# --------------------------------------------------------------------
# removing blocks
# --------------------------------------------------------------------

sub _remove_blocks {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $blocks = [];
    foreach my $block ( $sel_obj->blocks ) {
        push @$blocks, { name => $block->short_description, obj => $block };
    }
    _remove_items( $menu, $sel_obj, $tree_path, $blocks, "Blocks", "block" );

}

# --------------------------------------------------------------------
# removing teachers
# --------------------------------------------------------------------
sub _remove_teachers {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $teachers = [];
    foreach my $teacher ( $sel_obj->teachers ) {
        push @$teachers, { name => "$teacher", obj => $teacher };
    }
    _remove_items( $menu, $sel_obj, $tree_path, $teachers, "Teachers",
        "teacher" );
}

# --------------------------------------------------------------------
# removing streams
# --------------------------------------------------------------------
sub _remove_streams {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $streams = [];

    foreach my $stream ( $sel_obj->streams ) {
        push @$streams, { name => "$stream", obj => $stream };
    }
    _remove_items( $menu, $sel_obj, $tree_path, $streams, "Streams", "stream" );
}

# --------------------------------------------------------------------
# removing labs
# --------------------------------------------------------------------
sub _remove_labs {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;

    my $labs = [];

    foreach my $lab ( $sel_obj->labs ) {
        push @$labs, { name => "$lab", obj => $labs };
    }
    _remove_items( $menu, $sel_obj, $tree_path, $labs, "Labs", "lab" );
}

# --------------------------------------------------------------------
# remove all resources menu
# --------------------------------------------------------------------
sub _remove_all {
    my $menu      = shift;
    my $sel_obj   = shift;
    my $tree_path = shift;
    push @$menu,
      [
        'command',
        "Clear All Teachers, Labs, and Streams",
        -command => [ \&EditCourses::clear_all_from_obj1, $sel_obj, $tree_path ]
      ];
}

# --------------------------------------------------------------------
# Remove a single item
# --------------------------------------------------------------------
sub _remove_item {
    my ( $menu, $obj1, $obj2, $path, $title ) = @_;
    $path =~ s:^(.*)/.*$:$1:;
    push @$menu,
      [
        "command",
        $title,
        -command => [
            \&EditCourses::remove_obj2_from_obj1,
            $Schedule, $obj2, $obj1, $path
        ]
      ];
}

###################################################################
# sorting subs
###################################################################
sub _sort_by_number { $a->number <=> $b->number }

sub _sort_by_alphabet { $a->number cmp $b->number }

sub _sort_by_block_time {
    $a->day_number <=> $b->day_number
      || $a->start_number <=> $b->start_number;
}

sub _sort_by_block_id {
    $a->number <=> $b->number;
}

sub _sort_by_teacher_name {
    $a->lastname cmp $b->lastname
      || $a->firstname cmp $b->firstname;
}

1;
