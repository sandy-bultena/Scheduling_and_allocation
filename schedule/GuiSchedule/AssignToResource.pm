#!/usr/bin/perl
use strict;
use warnings;

package AssignToResource;
use FindBin;
use lib "$FindBin::Bin/..";
use Carp;
use Data::Dumper;
use GUI::AssignToResourceTk;

# =================================================================
# Class/Global Variables
# =================================================================
our $Max_id = 0;
my $Schedule;
my $Views_manager;
my %Styles;

my $Frame;
my $Day;
my $Start;
my $Duration;
my $Type;

my $Scheduable;

# ===================================================================
# globals
# ===================================================================
my $Course;
my $Section;
my $Block;
my $Teacher;
my $Lab;
my $Stream;
my $Gui;

my %dayName = (
                1 => "Monday",
                2 => "Tuesday",
                3 => "Wednesday",
                4 => "Thursday",
                5 => "Friday"
);

# ===================================================================
# new
# ===================================================================
sub new {
    my $class  = shift;
    my $viewTk = shift;

    $Schedule      = shift;
    $Views_manager = shift;

    $Day      = shift;
    $Start    = shift;
    $Duration = shift;

    $Scheduable = shift;
    $Type       = shift;

    $Frame = $viewTk->canvas;

    $Lab     = $Scheduable if $Type eq 'lab';
    $Teacher = $Scheduable if $Type eq 'teacher';
    $Stream  = $Scheduable if $Type eq 'stream';
    
    OpenDialog();
}

# ============================================================================
# OpenDialog
# ============================================================================
sub OpenDialog {
    print "Opening Dialog\n";
    if ($Schedule) {

        $Gui = AssignToResourceTk->new($Type);

        #------------------------------------
        # SET UP LAB DATA
        #------------------------------------
        my %lab_names;
        foreach my $lab ( $Schedule->labs->list ) {
            $lab_names{ $lab->id } = "$lab";
        }
        $Gui->list_labs( \%lab_names );

        #------------------------------------
        # SET UP TEACHER DATA
        #------------------------------------
        my %teacher_names;
        foreach my $teacher ( $Schedule->teachers->list ) {
            $teacher_names{ $teacher->id } = "$teacher";
        }
        $Gui->list_teachers( \%teacher_names );

        #------------------------------------
        # SET UP COURSE DATA
        #------------------------------------
        my %course_names;
        foreach my $course ( $Schedule->courses->list ) {
            $course_names{ $course->id } = $course->short_description;
        }
        $Gui->list_courses( \%course_names );

        #------------------------------------
        # SET UP SECTION DATA
        #------------------------------------
        my %section_names;
        $Gui->list_sections( \%section_names );

        #------------------------------------
        # SET UP BLOCK DATA
        #------------------------------------
        my %block_names;
        $Gui->list_blocks( \%block_names );

        #------------------------------------
        # setup event handlers
        #------------------------------------
        $Gui->cb_course_selected( \&_cb_course_selected );
        $Gui->cb_section_selected( \&_cb_section_selected );
        $Gui->cb_block_selected( \&_cb_block_selected );
        $Gui->cb_teacher_selected( \&_cb_teacher_selected );
        $Gui->cb_lab_selected(\&_cb_lab_selected);
        $Gui->cb_add_new_section( \&_add_new_section );
        $Gui->cb_add_new_block( \&_add_new_block );
        $Gui->cb_add_new_teacher (\&_add_new_teacher);
        $Gui->cb_add_new_lab (\&_add_new_lab);

        #------------------------------------
        # Create Dialog Box
        #------------------------------------
        my $title = "Assign block to " . ucfirst($Type);
        my $block_text =
            $dayName{$Day} . " at "
          . _hoursToString($Start) . " for "
          . $Duration
          . " hour(s)";

        $Gui->draw( $Frame, $title, );
        print "gui is drawn\n";

        #------------------------------------
        #Show menu
        #------------------------------------
        my $answer = $Gui->Show() || "Cancel";

        if ( $answer eq "Ok" ) {

            # check if a block is defined
            if ($Block) {

                #if it is, assign all the properties to the block and return
                $Block->day($Day);
                $Block->start( _hoursToString($Start) );
                $Block->duration($Duration);
                $Block->assign_lab($Lab)         if $Lab;
                $Block->assign_teacher($Teacher) if $Teacher;
                return 1;
            }
        }
        return 0;
    }
}

############################33
sub _cb_course_selected {
    print "in _cb_course_selected\n";

    # get course id and set global Course variable
    my $course_name = shift;
    my $id = _get_id ( $Gui->list_courses, $course_name );
    $Course = $Schedule->courses->get($id);

    # since we have a new course, we need to nullify the sections and blocks
    $Section = undef;
    $Block   = undef;
    $Gui->clear_sections_and_blocks();
    $Gui->enable_new_section_button();

    # what sections are available for this course ?
    my @sections = $Course->sections;

    # add to drop-down menu choices
    foreach my $i (@sections) {
        $Gui->list_sections->{ $i->id } = "$i";
    }
    print "Calling set_section_choices\n";
    $Gui->set_section_choices();

}

sub _cb_section_selected {

    # get section id and save global Section
    my $section_name = shift;
    my $id = _get_id ( $Gui->list_sections, $section_name );
    $Section = $Course->get_section_by_id($id);;

    # since we have a new section, we need to nullify the blocks
    $Gui->clear_blocks();
    $Gui->enable_new_block_button();

    # what blocks are available for this course ?
    my @blocks = $Section->blocks;

    # add to drop-down menu choices
    foreach my $i (@blocks) {
        $Gui->list_blocks->{ $i->id } = "$i";
    }
    $Gui->set_block_choices();

    # set the default teacher for this course/section if this
    # assign to resource type is NOT a teacher
    return if $Type eq 'teacher';

    my @teachers = $Section->teachers;
    if (@teachers) {
        $Teacher = $teachers[0];
        $Gui->set_teacher("$Teacher");
    }
}

sub _cb_block_selected {
    my $block_name = shift;
    my $id = _get_id ( $Gui->list_blocks, $block_name );
    $Block = $Section->get_block_by_id($id);
}

sub _cb_lab_selected {
    my $lab_name = shift;
    my $id = _get_id ( $Gui->list_lab, $lab_name );
    $Lab = $Schedule->labs->get($id);
}

# ============================================================================
# add_new_section
# ============================================================================
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
                           . "Section(s) by this name already exsist!\n"
                           . "Do you still want create this new section?\n\n"
                           . "The name of the section will be set to something unique"
        );

        #If not, set section to first instance of the section with
        #the section name
        if ( $answer eq 'No' ) {
            $Section = $sections[0];
            _cb_section_selected("$Section");
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
    $Gui->list_sections->{ $Section->id } = "$Section";
    _cb_section_selected("$Section");
    $Gui->set_section("$Section");

}

# ============================================================================
# add_new_block
# ============================================================================
sub _cb_add_new_block {

    my $name = shift;
    return unless $Course;
    return unless $Section;

    $Block = Block->new( -number => $Section->get_new_number );
    $Section->add_block($Block);
    $Gui->list_blocks->{ $Block->id } = $Block->short_description;
    $Gui->set_block( $Block->short_description );
}

sub _get_id {
    my $hash_ptr = shift;
    my $name     = shift;
    my %ref      = reverse %{$hash_ptr};
    return $ref{$name};
}

sub _reset_hash {
    my $hash_ptr;
    my $new_hash_ptr;

    %{$hash_ptr} = ();
    foreach my $key ( keys %$new_hash_ptr ) {
        $hash_ptr->{$key} = $new_hash_ptr->{$key};
    }
}


# ============================================================================
# add_new_lab
# ============================================================================
sub cb_add_new_lab {

    my $lab_name     = shift;
    my $lab_number = shift;

    return unless $lab_number;
    
    
        #see if a lab by that number exsits
        my $labNew = $Schedule->labs->get_by_number($lab_number);

        if ($labNew) {
                    my $question = $Gui->yes_no( "Lab already exists",
                                     "I won't let you do anything, ok?" );
        $Lab = undef;
        return;
        }
            

            $Lab = Lab->new( -number => $lab_number,
                                -descr  => $lab_name );

            $Schedule->labs->add($Lab);
            $Gui->list_labs->{ $labNew->id } = "$Lab";
            $Lab     = $labNew;
            $Gui->set_lab("$Lab");


}

# ============================================================================
# set lab
# ============================================================================
sub _cb_set_lab {
    my $id = shift;
    $Lab = $Schedule->labs->get($id);
}

# ============================================================================
# teacher was selected
# ============================================================================
sub _cb_teacher_selected {
    my $teacher_name = shift;
    my $id = _get_id { $Gui->list_teachers, $teacher_name };
    $Teacher = $Schedule->Teachers->get($id);
}

# ============================================================================
# add new teacher
# ============================================================================
sub _cb_add_new_teacher {

    my $self = shift;

    my $firstname = shift;
    my $lastname  = shift;
    my $teacher   = "";

    # Check is a first and last name are inputed, otherwise return
    return unless !$firstname || !$lastname;

    #see if a teacher by that name exsits
    $teacher = $Schedule->teachers->get_by_name( $firstname, $lastname );

    if ($teacher) {

        my $question = $Gui->yes_no( "Teacher already exists",
                                     "I won't let you do anything, ok?" );
        $Teacher = undef;
        return;
    }

    #if no teacher by the inputed name exists, create a new teacher
    $Teacher = Teacher->new( -firstname => $firstname,
                             -lastname  => $lastname );
    $Schedule->teachers->add($Teacher);

    $Gui->list_teachers->{ $Teacher->id } = "$Teacher";
    $Gui->set_teacher("$Teacher");
}

#=======================
#_hoursToString
#  8.5 -> 8:30
#=======================
sub _hoursToString {
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
