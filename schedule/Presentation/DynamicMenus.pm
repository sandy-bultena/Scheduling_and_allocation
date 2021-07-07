#!/usr/bin/perl
use strict;
use warnings;

package DynamicMenus;

my $Schedule;
my $Parent_presenter;

sub create_tree_menus {
    $Schedule = shift;
    my $selected_obj = shift;
    my $parent_obj   = shift;
    my $tree_path    = shift;

    my $type = $Schedule->get_object_type($selected_obj);

    #=====================================
    # What to show on course menu on tree object
    #=====================================
    my $menu = [];
    if ( $type eq 'course' ) {
        _add_teachers_menu( $menu, $selected_obj, $tree_path );
        _add_section_edit_course_menu( $menu, $selected_obj, $tree_path );
        _needs_allocation_menu( $menu, $selected_obj, $tree_path );
        _remove_teachers_menu( $menu, $selected_obj, $tree_path );
        _remove_all_menu( $menu, $selected_obj, $tree_path );
    }
    elsif ( $type eq 'section' ) {
        _add_teachers_menu( $menu, $selected_obj, $tree_path );
        _set_streams_menu( $menu, $selected_obj, $tree_path );
        _add_blocks_edit_section_menu( $menu, $selected_obj, $tree_path );
        _remove_teachers_menu( $menu, $selected_obj, $tree_path );
        _remove_streams_menu( $menu, $selected_obj, $tree_path );
        _remove_all_menu( $menu, $selected_obj, $tree_path );
    }
    elsif ( $type eq 'block' ) {
        _add_teachers_menu( $menu, $selected_obj, $tree_path );
        _set_labs_menu( $menu, $selected_obj, $tree_path );
        _remove_teachers_menu( $menu, $selected_obj, $tree_path );
        _remove_labs_menu( $menu, $selected_obj, $tree_path );
        _remove_all_menu( $menu, $selected_obj, $tree_path );
    }
    elsif ( $type eq 'teacher' ) {
        _teacher_menu( $menu, $selected_obj, $parent_obj, $tree_path );
    }
    elsif ( $type eq 'lab' ) {
        _lab_menu( $menu, $selected_obj, $parent_obj, $tree_path );
    }
    return $menu;

}

sub show_scheduable_menu {
    my $Schedule        = shift;
    my $selected_obj_id = shift;
    my $type            = shift;
    my $selected_obj    = $Schedule->get_object_by_id_and_type($selected_obj_id,$type);

    my $menu    = [];
    my $courses = [];
    push @$menu,
      [ 'cascade', "Add $type to Course", -tearoff => 0, -menuitems => $courses ];

    # courses
    foreach my $course ( sort { &_sort_by_alphabet }
        $Schedule->courses->list )
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
                    $selected_obj,
                    "Schedule/Course" . $course->id,
                ]
              ];
        }

        # sections
        foreach my $section ( sort {&_sort_by_number }
            $course->sections )
        {
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
                    $selected_obj,
                    "Schedule/Course" . $course->id . "/Section" . $section->id
                ]
              ];

            # blocks
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
                            $selected_obj,
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
# adding teachers
# --------------------------------------------------------------------
sub _add_teachers_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $tree_path    = shift;

    my $teacher_menu = [];
    foreach my $teacher ( $Schedule->all_teachers ) {
        push @$teacher_menu,
          [
            "command",
            "$teacher",
            -command => [
                \&EditCourses::assign_obj2_to_obj1,
                $selected_obj, $teacher, $tree_path
            ]
          ];
    }
    push @$menu,
      [
        "cascade", "Add Teacher",
        -tearoff   => 0,
        -menuitems => $teacher_menu
      ];
}

# --------------------------------------------------------------------
# setting labs
# --------------------------------------------------------------------
sub _set_labs_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $tree_path    = shift;

    my $lab_menu = [];
    foreach my $lab ( $Schedule->all_labs ) {
        next if $selected_obj->has_lab($lab);
        push @$lab_menu,
          [
            "command",
            "$lab",
            -command => [
                \&EditCourses::assign_obj2_to_obj1,
                $selected_obj, $lab, $tree_path
            ]
          ];
    }
    push @$menu,
      [ "cascade", "Set Lab", -tearoff => 0, -menuitems => $lab_menu ];
}

# --------------------------------------------------------------------
# setting streams
# --------------------------------------------------------------------
sub _set_streams_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $tree_path    = shift;

    my $stream_menu = [];
    foreach my $stream ( $Schedule->all_streams ) {
        push @$stream_menu,
          [
            "command",
            "$stream",
            -command => [
                \&EditCourses::assign_obj2_to_obj1,
                $selected_obj, $stream, $tree_path
            ]
          ];
    }
    push @$menu,
      [
        "cascade", "Set Stream",
        -tearoff   => 0,
        -menuitems => $stream_menu
      ];
}

# --------------------------------------------------------------------
# add blocks, edit section
# --------------------------------------------------------------------
sub _add_blocks_edit_section_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $tree_path;

    push @$menu,
      [
        'command',
        "Add Blocks",
        -command =>
          [ \&EditCourse::add_blocks_dialog, $selected_obj, $tree_path ]
      ];
    push @$menu,
      [
        'command',
        "Edit Section",
        -command =>
          [ \&EditCourses::edit_section_dialog, $selected_obj, $tree_path ]
      ];
    push @$menu, "separator";
}

# --------------------------------------------------------------------
# add sections, edit course
# --------------------------------------------------------------------
sub _add_section_edit_course_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $tree_path;
    push @$menu,
      [
        'command',
        "Add Sections(s)",
        -command =>
          [ \&EditCourses::add_section_dialog, $selected_obj, $tree_path ]
      ];

    push @$menu,
      [
        'command',
        "Edit Course",
        -command =>
          [ \&EditCourses::edit_course_dialog, $selected_obj, $tree_path ]
      ];
    push @$menu, "separator";
}

# --------------------------------------------------------------------
# needs allocation
# --------------------------------------------------------------------
sub _needs_allocation_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $tree_path    = shift;
    if ( $selected_obj->needs_allocation ) {
        push @$menu, [
            "command",
            "unset 'needs allocation'",
            -command => sub {
                $selected_obj->needs_allocation(0);
                EditCourses::set_dirty();
            },
        ];
    }
    else {
        push @$menu, [
            "command",
            "set 'needs allocation'",
            -command => sub {
                $selected_obj->needs_allocation(1);
                EditCourses::set_dirty();
            },
        ];
    }
    push @$menu, "separator";
}

# --------------------------------------------------------------------
# removing teachers
# --------------------------------------------------------------------
sub _remove_teachers_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $tree_path    = shift;

    my $rem_teacher_menu = [];
    push @$rem_teacher_menu,
      [
        "command",
        "All Teachers",
        -command => [
            \&EditCourses::remove_all_types_from_obj1,
            $selected_obj, 'teacher', $tree_path
        ]
      ];
    push @$rem_teacher_menu, "separator";

    foreach my $teacher ( $selected_obj->teachers ) {
        push @$rem_teacher_menu,
          [
            "command",
            "$teacher",
            -command => [
                \&EditCourses::remove_obj2_from_obj1,
                $selected_obj, $teacher, $tree_path
            ]
          ];
    }
    push @$menu,
      [
        "cascade", "Remove Teachers",
        -tearoff   => 0,
        -menuitems => $rem_teacher_menu
      ];
}

# --------------------------------------------------------------------
# removing streams
# --------------------------------------------------------------------
sub _remove_streams_menu {
    my $menu            = shift;
    my $selected_obj    = shift;
    my $tree_path       = shift;
    my $rem_stream_menu = [];

    push @$rem_stream_menu,
      [
        "command",
        "All Streams",
        -command => [
            \&EditCourses::remove_all_types_from_obj1,
            $selected_obj, 'stream', $tree_path
        ]
      ];
    push @$rem_stream_menu, "separator";

    foreach my $stream ( $selected_obj->streams ) {
        push @$rem_stream_menu,
          [
            "command",
            "$stream",
            -command => [
                \&EditCourses::remove_obj2_from_obj1,
                $selected_obj, $stream, $tree_path
            ]
          ];
    }
    push @$menu,
      [
        "cascade", "Remove Streams",
        -tearoff   => 0,
        -menuitems => $rem_stream_menu
      ];
}

# --------------------------------------------------------------------
# removing labs
# --------------------------------------------------------------------
sub _remove_labs_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $parent_obj   = shift;
    my $tree_path    = shift;
    my $rem_lab_menu = [];

    push @$rem_lab_menu,
      [
        "command",
        "All labs",
        -command => [
            \&EditCourses::remove_all_types_from_obj1,
            $selected_obj, "lab", $tree_path
        ]
      ];
    push @$rem_lab_menu, "separator";

    foreach my $lab ( $selected_obj->labs ) {
        push @$rem_lab_menu,
          [
            "command",
            "$lab",
            -command => [
                \&EditCourses::remove_obj2_from_obj1,
                $selected_obj, $lab, $tree_path
            ]
          ];
    }
    push @$menu,
      [
        "cascade", "Remove labs",
        -tearoff   => 0,
        -menuitems => $rem_lab_menu
      ];
}

# --------------------------------------------------------------------
# remove all resources menu
# --------------------------------------------------------------------
sub _remove_all_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $tree_path    = shift;
    push @$menu,
      [
        'command',
        "Clear All Teachers, Labs, and Streams",
        -command =>
          [ \&EditCourses::clear_all_from_obj1, $selected_obj, $tree_path ]
      ];
}

# --------------------------------------------------------------------
# Teacher Menu
# --------------------------------------------------------------------
sub _teacher_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $parent_obj   = shift;
    my $tree_path    = shift;
    push @$menu,
      [
        "command",
        "Remove",
        -command => [
            \&EditCourses::remove_obj2_from_obj1,
            $parent_obj, $selected_obj, $tree_path
        ]
      ];
}

# --------------------------------------------------------------------
# Lab Menu
# --------------------------------------------------------------------
sub _lab_menu {
    my $menu         = shift;
    my $selected_obj = shift;
    my $parent_obj   = shift;
    my $tree_path    = shift;
    push @$menu,
      [
        "command",
        "Remove",
        -command => [
            \&EditCourses::remove_obj2_from_obj1,
            $parent_obj, $selected_obj, $tree_path
        ]
      ];
}

###################################################################
# sorting subs
###################################################################
sub _sort_by_number { $a->number <=> $b->number }

sub _sort_by_alphabet {$a->number cmp $b->number }

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
