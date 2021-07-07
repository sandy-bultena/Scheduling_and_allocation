#!/usr/bin/perl
use strict;
use warnings;


# =================================================================
# make dialog box for editing courses
# =================================================================
sub new_course_dialog {
    my $frame = shift;
    my $tl    = $frame->Toplevel( -title => "New Course" );
    my $self  = { -toplevel => $tl };

    # ---------------------------------------------------------------
    # instructions
    # ---------------------------------------------------------------
    $tl->Label(
        -text => "New Course",
        -font => [qw/-family arial -size 18/]
    )->pack( -pady => 10 );

    # ---------------------------------------------------------------
    # buttons
    # ---------------------------------------------------------------
    my $button_row =
      $tl->Frame()
      ->pack( -side => 'bottom', -expand => 1, -fill => 'y', -pady => 15 );
    $button_row->Button(
        -text    => 'Add Block',
        -width   => 12,
        -command => [ \&_add_block_to_editor, $self ]
    )->pack( -side => 'left', -pady => 3 );

    $self->{-remove_block_button} = $button_row->Button(
        -text    => 'Remove Block',
        -width   => 12,
        -command => [ \&_remove_block_to_editor, $self ],
        -state   => 'disabled'
    )->pack( -side => 'left', -pady => 3 );

    $self->{-new} = $button_row->Button(
        -text    => 'Create',
        -width   => 12,
        -command => [ \&save_course_modified, $self, 1, $tl ]
    )->pack( -side => 'left', -pady => 3 );

    $self->{-new} = $button_row->Button(
        -text    => "Create and Edit",
        -width   => 12,
        -command => sub {
            my $obj = save_course_modified( $self, 1, $tl );
            _edit_course_dialog( $tree, $tree, $obj,
                "Schedule/Course" . $obj->id );
        }
    )->pack( -side => 'left', -pady => 3 );

    $self->{-cancel} = $button_row->Button(
        -text    => 'Cancel',
        -width   => 12,
        -command => sub { $tl->destroy(); }
    )->pack( -side => 'left', -pady => 3 );

    # ---------------------------------------------------------------
    # info data
    # ---------------------------------------------------------------
    my $info_row = $self->{-info_row} =
      $tl->Frame()->pack( -side => 'top', -expand => 1, -fill => 'both' );

    # ---------------------------------------------------------------
    # Course Info Labels
    # ---------------------------------------------------------------
    $info_row->Label(
        -text   => "Number",
        -anchor => 'e'
    )->grid( -column => 0, -row => 0, -sticky => 'nwes' );
    $info_row->Label(
        -text   => "Description",
        -anchor => 'e'
    )->grid( -column => 0, -row => 1, -sticky => 'nwes' );

    #$info_row->Label(
    #	-text   => "Hours per week",
    #	-anchor => 'e'
    #)->grid( -column => 0, -row => 2, -sticky => 'nwes' );

    # ---------------------------------------------------------------
    # Course Info Entry boxes
    # ---------------------------------------------------------------
    $self->{-number} =
      $info_row->Entry( -width => 6 )
      ->grid( -column => 1, -row => 0, -sticky => 'nwes' );

    $self->{-name} =
      $info_row->Entry( -width => 30 )
      ->grid( -column => 1, -row => 1, -sticky => 'nwes' );

    #$self->{-course_hours} = $info_row->Entry(
    #	-width           => 6,
    #	-validate        => 'key',
    #	-validatecommand => \&is_number,
    #	-invalidcommand  => sub { $info_row->bell },
    #)->grid( -column => 1, -row => 2, -sticky => 'nwes' );

    # make the "Enter" key mimic Tab key
    $self->{-number}->bind( "<Key-Return>",
        sub { $self->{-number}->eventGenerate("<Tab>") } );
    $self->{-name}
      ->bind( "<Key-Return>", sub { $self->{-name}->eventGenerate("<Tab>") } );

    #$self->{-course_hours}->bind(
    #	"<Key-Return>",
    #	sub {
    #		$self->{-course_hours}->eventGenerate("<Tab>");
    #	}
    #);

    # ---------------------------------------------------------------
    # Section Info
    # ---------------------------------------------------------------
    $info_row->Label(
        -text   => "Sections",
        -anchor => 'e'
    )->grid( -column => 0, -row => 3, -sticky => 'nwes' );

    $self->{-sections} = $info_row->Entry(
        -width           => 5,
        -validate        => 'key',
        -validatecommand => \&is_number,
        -invalidcommand  => sub { $info_row->bell },
    )->grid( -column => 1, -row => 3, -sticky => 'nwes' );

    # make the "Enter" key mimic Tab key
    $self->{-sections}->bind( "<Key-Return>",
        sub { $self->{-sections}->eventGenerate("<Tab>") } );

    # ---------------------------------------------------------------
    # Block Info
    # ---------------------------------------------------------------
    $info_row->Label(
        -text   => 'Block Hours:',
        -anchor => 'se',
        -height => 2
    )->grid( -column => 0, -row => 4 );
    _add_block_to_editor( $self, 1 );

    return bless $self;
}

# ---------------------------------------------------------------
# add a block row to the editor
# ---------------------------------------------------------------
{
    my $num;

    sub _add_block_to_editor {
        my $self      = shift;
        my $input_num = shift;
        $num = 0 unless $num;
        $num++;
        $num = $input_num if defined $input_num;
        my $rmBTN = $self->{-remove_block_button};

        if ( $num > 1 ) {
            $rmBTN->configure( -state => 'normal' );
        }

        my $info_row = $self->{-info_row};

        $self->{-blockNums} = [] unless $self->{-blockNums};

        my $l = $info_row->Label(
            -text   => "$num",
            -anchor => 'e'
        )->grid( -column => 0, -row => 4 + $num, -sticky => 'nwes' );
        push @{ $self->{-blockNums} }, $l;

        $self->{-hours} = [] unless $self->{-hours};

        my $e = $info_row->Entry(
            -width           => 15,
            -validate        => 'key',
            -validatecommand => \&is_number,
            -invalidcommand  => sub { $info_row->bell },
        )->grid( -column => 1, -row => 4 + $num, -sticky => 'nwes' );

        push @{ $self->{-hours} }, $e;
        $e->focus;

        # make the "Enter" key mimic Tab key
        $e->bind( "<Key-Return>", sub { $e->eventGenerate("<Tab>") } );

    }

    sub _remove_block_to_editor {
        my $self      = shift;
        my $input_num = shift;
        my $info_row  = $self->{-info_row};
        my $rmBTN     = $self->{-remove_block_button};

        if ( $num <= 1 ) {
            my $Error = $info_row->Dialog(
                -title          => 'Error',
                -text           => "Can't remove block.",
                -default_button => 'Okay',
                -buttons        => ['Okay']
            )->Show();
            return;
        }

        $num--;

        if ( $num <= 1 ) {
            $rmBTN->configure( -state => 'disabled' );
        }

        my $tempL = pop @{ $self->{-blockNums} };
        my $tempH = pop @{ $self->{-hours} };
        $tempH->destroy if Tk::Exists($tempH);
        $tempL->destroy if Tk::Exists($tempL);
        $info_row->update;
    }
}


# =================================================================
# validate that number be entered in a entry box is a real number
# (positive real number)
# =================================================================
sub is_number {
    my $n = shift;
    return 1 if $n =~ (/^(\s*\d*\.?\d*\s*|)$/);
    return 0;
}

# =================================================================
# validate that number be entered in a entry box is a whole number
# (positive integer)
# =================================================================
sub is_integer {
    my $n = shift;
    return 1 if $n =~ /^(\s*\d+\s*|)$/;
    return 0;
}

# ================================================================
# Validate that the course number is new/unique
# (alway return true, just change input to red and disable close button)
# ================================================================
sub _unique_number {

    #no warnings;
    my $oldName   = shift;
    my $button    = shift;
    my $entry     = ${ +shift };
    my $message   = ${ +shift };
    my $toCompare = shift;
    if ($entry) {
        if (   $toCompare ne $oldName
            && $Schedule->courses->get_by_number($toCompare) )
        {
            $button->configure( -state => 'disabled' );
            $entry->configure( -bg => 'red' );
            $message->configure( -text => "Number Not Unique" );
            $entry->bell;
        }
        else {
            $button->configure( -state => 'normal' );
            $entry->configure( -bg => 'white' );
            $message->configure( -text => "" );
        }
    }

    return 1;
}

# =================================================================
# save modified course
# returns course
# =================================================================
sub save_course_modified {
    my $edit_dialog = shift;
    my $new         = shift;
    my $course;
    my $tl = shift;

    #--------------------------------------------
    # Check that all elements are filled in
    #--------------------------------------------
    if (   $edit_dialog->{-number}->get eq ""
        || $edit_dialog->{-name}->get eq ""
        || $edit_dialog->{-sections}->get eq "" )
    {
        $tl->messageBox(
            -title   => 'Error',
            -message => "Missing elements"
        );
        return;
    }

    foreach my $blnum ( 1 .. scalar( @{ $edit_dialog->{-hours} } ) ) {
        if ( $edit_dialog->{-hours}[ $blnum - 1 ]->get eq "" ) {
            $tl->messageBox(
                -title   => 'Error',
                -message => "Missing elements"
            );
            return;
        }

    }

    # get course number
    my $number = $edit_dialog->{-number}->get;

    # if new, or if course ID has been modified, verify it's uniqueness
    if ( $new || $number ne $edit_dialog->{-inital_number} ) {
        $course = $Schedule->courses->get_by_number($number);
        if ($course) {
            $tree->toplevel->messageBox(
                -title   => 'Edit Course',
                -message => 'Course Number is NOT unique!',
                -type    => 'OK',
                -icon    => 'error'
            );
            $edit_dialog->{-toplevel}->raise;
            return;
        }
    }

    # get existing course object if not 'new'
    $course =
      $Schedule->courses->get_by_number( $edit_dialog->{-inital_number} )
      unless $new;

    # if no object, must create a new course
    unless ($course) {
        $course = Course->new( -number => $number );
        $Schedule->courses->add($course);
    }

    # set the properties
    $course->number($number);
    $course->name( $edit_dialog->{-name}->get );

    # go through each section
    foreach my $num ( 1 .. $edit_dialog->{-sections}->get ) {

        # if section already exists, skip it
        my $sec = $course->get_section($num);
        next if $sec;

        # create new section
        $sec = Section->new( -number => $num );
        $course->_add_section($sec);

        # for each section, add the blocks
        foreach my $blnum ( 1 .. scalar( @{ $edit_dialog->{-hours} } ) ) {
            my $bl = Block->new( -number => $sec->get_new_number );
            $bl->duration( $edit_dialog->{-hours}[ $blnum - 1 ]->get );
            $sec->_add_block($bl);
        }

    }

    # remove any excess sections
    foreach my $num (
        $edit_dialog->{-sections}->get + 1 .. $course->max_section_number )
    {
        my $sec = $course->get_section($num);
        $course->remove_section($sec) if $sec;
    }

    # update schedule and close this window
    $edit_dialog->{-toplevel}->destroy;
    _refresh_schedule_gui($tree);
    $tree->autosetmode();
    _set_dirty();
    return $course;
}




