#!/usr/bin/perl
use strict;
use warnings;

=head1 NAME

AssignToResource - Create or Assign Time Blocks to various resources 

=head1 VERSION

Version 6.00

=head1 SYNOPSIS

    use Tk;
    use Schedule;
    my $mw = MainWindow->new();
    my $s = Schedule->read_YAML("my_schedule.yaml");
    my $t = $Schedule->teachers->get_by_name("Jane","Doe");
    
    # maybe assign block thurs 10:30-13:30 to Jane Doe ?
    AssignToResourcen( $mw, $s, 3, 10.5, 3, $t );

=head1 DESCRIPTION

Called with a date/time/duration of a block, as well as a Teacher/Lab.

Allows the user to assign this block to a Course and Section, 

or to create a new block, 

or assign an existing block to Course and Section.

=head1 METHODS

=cut

package AssignToResource;
use FindBin;
use lib "$FindBin::Bin/..";
use Carp;
use GUI::AssignToResourceTk;

# =================================================================
# Class/Global Variables
# =================================================================
my $Schedule;

my $mw;
my $Type;

# ===================================================================
# globals
# ===================================================================
my $Course;
my $Section;
my $Block;
my $Teacher;
my $Lab;
my $Gui;

my %Day_name = (
                 1 => "Monday",
                 2 => "Tuesday",
                 3 => "Wednesday",
                 4 => "Thursday",
                 5 => "Friday"
);

# ===================================================================
# Constructor
# ===================================================================

=head2 new

Creates and manages a gui that will allow the user to assign a block to
various resources

B<Parameters>

- mw => the main gui window

- Schedule => schedule object

- day, start, duration => new block information

- scheduable => Teacher/Lab (if it is a Stream object, nothing will happen)

=cut

my $Day;
my $Start;
my $Duration;

sub new {
    my $class = shift;
    $mw = shift;

    $Schedule = shift;

    $Day      = shift;
    $Start    = shift;
    $Duration = shift;

    my $scheduable = shift;
    $Type = $Schedule->get_scheduable_object_type($scheduable);

    $Lab     = $scheduable if $Type eq 'lab';
    $Teacher = $scheduable if $Type eq 'teacher';
    return if $Type eq 'stream';

    #------------------------------------
    # Create Dialog Box
    #------------------------------------
    my $title = "Assign block to " . ucfirst($Type);
    my $block_text =
        $Day_name{$Day} . " at "
      . _hours_to_string($Start) . " for "
      . $Duration
      . " hour(s)";

    $Gui = AssignToResourceTk->new($Type);
    $Gui->draw( $mw, $title, $block_text );

    #------------------------------------
    # open dialog
    #------------------------------------
    _open_dialog() if $Schedule;
}

# ============================================================================
# OpenDialog
# ============================================================================
sub _open_dialog {

    #------------------------------------
    # setup event handlers
    #------------------------------------
    $Gui->cb_course_selected( \&_cb_course_selected );
    $Gui->cb_section_selected( \&_cb_section_selected );
    $Gui->cb_block_selected( \&_cb_block_selected );
    $Gui->cb_teacher_selected( \&_cb_teacher_selected );
    $Gui->cb_lab_selected( \&_cb_lab_selected );

    $Gui->cb_add_new_section( \&_cb_add_new_section );
    $Gui->cb_add_new_block( \&_cb_add_new_block );
    $Gui->cb_add_new_teacher( \&_cb_add_new_teacher );
    $Gui->cb_add_new_lab( \&_cb_add_new_lab );

    #------------------------------------
    # get lists of resources
    #------------------------------------

    # labs
    my %lab_names;
    foreach my $lab ( $Schedule->labs->list ) {
        $lab_names{ $lab->id } = "$lab";
    }
    $Gui->set_lab_choices( \%lab_names );

    # teachers
    my %teacher_names;
    foreach my $teacher ( $Schedule->teachers->list ) {
        $teacher_names{ $teacher->id } = "$teacher";
    }
    $Gui->set_teacher_choices( \%teacher_names );

    # courses
    my %course_names;
    foreach my $course ( $Schedule->courses->list ) {
        $course_names{ $course->id } = $course->short_description;
    }
    $Gui->set_course_choices( \%course_names );

    #------------------------------------
    # Show dialog
    #------------------------------------
    my $answer = $Gui->Show() || "Cancel";

    #------------------------------------
    # assign block to resource
    #------------------------------------
    if ( $answer eq "Ok" ) {

        # check if a block is defined
        if ($Block) {

            #if it is, assign all the properties to the block and return
            $Block->day($Day);
            $Block->start( _hours_to_string($Start) );
            $Block->duration($Duration);
            $Block->assign_lab($Lab)         if $Lab;
            $Block->assign_teacher($Teacher) if $Teacher;
            return 1;
        }
    }
    return 0;
}

# ============================================================================
# callbacks
# ============================================================================

# ----------------------------------------------------------------------------
# course was selected
# ----------------------------------------------------------------------------
sub _cb_course_selected {

    # get course id and set global Course variable
    my $id = shift;
    $Course = $Schedule->courses->get($id);

    # since we have a new course, we need to nullify the sections and blocks
    $Section = undef;
    $Block   = undef;
    $Gui->clear_sections_and_blocks();
    $Gui->enable_new_section_button();

    # what sections are available for this course ?
    my @sections = $Course->sections;
    my %sections;
    foreach my $i (@sections) {
        $sections{ $i->id } = "$i";
    }
    $Gui->set_section_choices( \%sections );

}

# ----------------------------------------------------------------------------
# section was selected
# ----------------------------------------------------------------------------
sub _cb_section_selected {

    # get section id and save global Section
    my $id = shift;
    $Section = $Course->get_section_by_id($id);

    # since we have a new section, we need to nullify the blocks
    $Gui->clear_blocks();
    $Gui->enable_new_block_button();

    # what blocks are available for this course/section ?
    my @blocks = $Section->blocks;
    my %blocks;
    foreach my $i (@blocks) {
        $blocks{ $i->id } = "$i";
    }
    $Gui->set_block_choices( \%blocks );

    # set the default teacher for this course/section if this
    # assign to resource type is NOT a teacher
    return if $Type eq 'teacher';

    my @teachers = $Section->teachers;
    if (@teachers) {
        $Teacher = $teachers[0];
        $Gui->set_teacher("$Teacher");
    }
}

# ----------------------------------------------------------------------------
# block was selected
# ----------------------------------------------------------------------------
sub _cb_block_selected {
    my $id = shift;
    $Block = $Section->get_block_by_id($id);
}

# ----------------------------------------------------------------------------
# lab was selected
# ----------------------------------------------------------------------------
sub _cb_lab_selected {
    my $id = shift;
    $Lab = $Schedule->labs->get($id);
}

# ----------------------------------------------------------------------------
# teacher was selected
# ----------------------------------------------------------------------------
sub _cb_teacher_selected {
    my $id = shift;
    $Teacher = $Schedule->Teachers->get($id);
}

# ----------------------------------------------------------------------------
# add_new_section
# ----------------------------------------------------------------------------
sub _cb_add_new_section {

    my $name = shift;
    return unless $Course;

    #check to see if a section by that name  exists
    my @sections = $Course->get_section_by_name($name);
    my $sectionNew;

    # --------------------------------------------------------------------
    # sections with this name already exist
    # --------------------------------------------------------------------
    if (@sections) {
        my $answer = $Gui->yes_no(
                         "Section already exists",
                         scalar @sections
                           . " section(s) by this name already exsist!\n"
                           . "Do you still want create this new section?\n\n"
                           . "The name of the section will be set to something unique"
        );

        #If not, set section to first instance of the section with
        #the section name
        if ( $answer eq 'No' ) {
            $Section = $sections[0];
            _cb_section_selected( $Section->id );
            $Gui->set_section("$Section");
            return;
        }
    }

    # --------------------------------------------------------------------
    # create new section
    # --------------------------------------------------------------------
    $Section = Section->new(
                             -number => $Course->get_new_number,
                             -hours  => 0,
                             -name   => $name
    );
    $Course->add_section($Section);

    # --------------------------------------------------------------------
    # add the new section to the drop down list, and make it the
    # selected section
    # --------------------------------------------------------------------
    # add to drop-down menu choices
    my %sections;
    @sections = $Course->sections;
    foreach my $i (@sections) {
        $sections{ $i->id } = "$i";
    }
    $Gui->set_section_choices( \%sections );

    $Gui->set_section("$Section");
    _cb_section_selected( $Section->id );

}

# ----------------------------------------------------------------------------
# add_new_block
# ----------------------------------------------------------------------------
sub _cb_add_new_block {

    my $name = shift;
    return unless $Course;
    return unless $Section;

    $Block = Block->new( -number => $Section->get_new_number );
    $Section->add_block($Block);
    $Block->day($Day);
    $Block->start( _hours_to_string($Start) );
    $Block->duration($Duration);

    my @blocks = $Section->blocks;
    my %blocks;
    foreach my $i (@blocks) {
        $blocks{ $i->id } = $i->short_description;
    }
    $Gui->set_block_choices( \%blocks );
    $Gui->set_block($Block);

}

# ----------------------------------------------------------------------------
# add_new_lab
# ----------------------------------------------------------------------------
sub _cb_add_new_lab {

    my $lab_name   = shift;
    my $lab_number = shift;

    return unless $lab_number;

    #see if a lab by that number exsits
    my $labNew = $Schedule->labs->get_by_number($lab_number);

    if ($labNew) {
        my $question = $Gui->yes_no( "Create new Lab",
                  "Lab already exists\n" . "I won't let you do anything, ok?" );
        $Lab = undef;
        return;
    }

    $Lab = Lab->new( -number => $lab_number,
                     -descr  => $lab_name );

    $Schedule->labs->add($Lab);

    my %lab_names;
    foreach my $lab ( $Schedule->labs->list ) {
        $lab_names{ $lab->id } = "$lab";
    }
    $Gui->set_lab_choices( \%lab_names );
    $Gui->set_lab("$Lab");

}

# ----------------------------------------------------------------------------
# add new teacher
# ----------------------------------------------------------------------------
sub _cb_add_new_teacher {

    my $firstname = shift;
    my $lastname  = shift;
    my $teacher   = "";

    # Check is a first and last name are inputed, otherwise return
    return if !$firstname || !$lastname;

    #see if a teacher by that name exsits
    $teacher = $Schedule->teachers->get_by_name( $firstname, $lastname );

    if ($teacher) {

        my $question = $Gui->yes_no( "Create new Teacher",
              "Teacher already exists\n" . "I won't let you do anything, ok?" );
        $Teacher = undef;
        return;
    }

    #if no teacher by the inputed name exists, create a new teacher
    $Teacher = Teacher->new( -firstname => $firstname,
                             -lastname  => $lastname );
    $Schedule->teachers->add($Teacher);

    my %teacher_names;
    foreach my $teacher ( $Schedule->teachers->list ) {
        $teacher_names{ $teacher->id } = "$teacher";
    }
    $Gui->set_teacher_choices( \%teacher_names );
    $Gui->set_teacher("$Teacher");
}

# ----------------------------------------------------------------------------
# _hours_to_string: 8.5 -> 8:30
# ----------------------------------------------------------------------------
sub _hours_to_string {
    my $time = shift;

    my $string = int($time) . ":";
    $string = $string . "00" if $time == int($time);
    $string = $string . "30" unless $time == int($time);

    return $string;

}

# =================================================================
# footer
# =================================================================

=head1 AUTHORS

Sandy Bultena, Alex Oxorn

=head1 COPYRIGHT

Copyright (c) 2021, Sandy Bultena, Alex Oxorn.

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;
