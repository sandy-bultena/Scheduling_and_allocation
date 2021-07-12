#!/usr/bin/perl
use strict;
use warnings;

package AddEditSectionAdvancedDialogTk;

sub new {
    my $class = shift;
    my $self = bless {}, $class;
    
    
}

sub _edit_section_dialog {
    my $frame = shift;
    my $tree  = shift;
    my $obj   = shift;
    my $path  = shift;

    my $change = 0;

    #--------------------------------------------------------
    # Defining Menu Lists
    #--------------------------------------------------------
    my $objPar = $obj->course;
    my $parent = $tree->info( 'parent', $path );
    
    my $cNum = $obj->number;

    my $cName = $obj->name;
    my $oldName = $cName || "";

    my $curBlock = "";

    my @blocks = $obj->blocks;
    my %blockName;
    foreach my $i (@blocks) {
        $blockName{ $i->id } = $i->print_description2;
    }

    my @teachersN = $Schedule->all_teachers;
    my $curTeachN = "";

    my %teacherNameN;
    foreach my $i (@teachersN) {
        $teacherNameN{ $i->id } = $i->firstname . " " . $i->lastname;
    }

    my @teachersO = $obj->teachers;
    my $curTeachO = "";
    
    my $hoursO = $obj->hours; 
    my $hoursN = $hoursO;  

    my %teacherNameO;
    foreach my $i (@teachersO) {
        $teacherNameO{ $i->id } = $i->firstname . " " . $i->lastname;
    }

    my @streamsN   = $Schedule->all_streams;
    my $curStreamN = "";
    my %streamNameN;
    foreach my $i (@streamsN) {
        $streamNameN{ $i->id } = $i->print_description2;
    }

    my @streamsO   = $obj->streams;
    my $curStreamO = "";
    my %streamNameO;
    foreach my $i (@streamsO) {
        $streamNameO{ $i->id } = $i->print_description2;
    }

    #--------------------------------------------------------
    # Defining Frames and widget names
    #--------------------------------------------------------

    my $edit_dialog = $frame->DialogBox(
                     -title => $obj->course->name . ": Section " . $obj->number,
                     -buttons => [ 'Close', 'Delete' ] );

    my $top = $edit_dialog->Subwidget("top");

    #my $frame1  = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );
    #my $frame2  = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );
    #my $frame2B = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );
    #my $frame3  = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );
    #my $frame3A = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );
    #my $frame3B = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );
    #my $frame4  = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );
    #my $frame4A = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );
    #my $frame4B = $edit_dialog->Frame( -height => 30, )->pack( -fill => 'x' );

    my $hoursEntry;
    my $blockDrop;
    my $blockText;
    my $blockAdd;
    my $blockRem;
    my $blockEdit;
    my $blockMessage;
    my $teachDropN;
    my $teachTextN;
    my $teachDropO;
    my $teachTextO;
    my $teachAdd;
    my $teachRem;
    my $teachMessage;
    my $streamDropO;
    my $streamTextO;
    my $streamDropN;
    my $streamTextN;
    my $streamAdd;
    my $streamRem;
    my $streamMessage;

    my $pad = 40;

    #--------------------------------------------------------
    # Block Add/Remove/Edit
    #--------------------------------------------------------

    $top->Label( -text => "Section Name", -anchor => 'w' )
      ->grid( $top->Entry( -textvariable => \$cName ),
              '-', '-', -sticky => "nsew" );

    $top->Label(-text=>"Hours",-anchor=>'w')
    ->grid($top->Entry(-textvariable => \$hoursN),
    $top->Label(-text=>"only used if there are no blocks"),"-",-sticky=>'nsew');

    $top->Label( -text => "" )->grid( -columnspan => 4 );

    $blockDrop = $top->JBrowseEntry(
                                     -variable => \$curBlock,
                                     -state    => 'readonly',
                                     -choices  => \%blockName,
                                     -width    => 12
                                   )->grid( -column => 1, -row => 2, -sticky => 'nsew', -ipadx => $pad );
    my $blockDropEntry = $blockDrop->Subwidget("entry");
    $blockDropEntry->configure( -disabledbackground => "white" );
    $blockDropEntry->configure( -disabledforeground => "black" );

    $blockText = $top->Label(
                              -text   => "Block: ",
                              -anchor => 'w'
                            )->grid( -column => 0, -row => 2, -sticky => 'nsew' );

    $blockAdd = $top->Button(
        -text    => "Add Block(s)",
        -command => sub {
            my $answer = _add_block( $top, $tree, $obj, $path );
            $answer = "Cancel" unless $answer;
            if ( $answer ne "Cancel" ) {
                $blockMessage->configure( -text => "Block(s) Added" );
                $top->bell;
                $curBlock = "";
                my @blocks2 = $obj->blocks;
                my %blockName2;
                foreach my $i (@blocks2) {
                    $blockName2{ $i->id } = $i->print_description2;
                }
                @blocks    = @blocks2;
                %blockName = %blockName2;
                $blockDrop->configure( -choices => \%blockName );
                $blockDrop->update;
                $change = 1;
            }
            else {
                $blockMessage->configure( -text => "" );
            }
        }
    )->grid( -column => 2, -row => 3, -sticky => 'nsew', -columnspan => 2 );

    $blockRem = $top->Button(
        -text    => "Remove Block",
        -command => sub {
            if ( $curBlock ne "" ) {
                my %rHash    = reverse %blockName;
                my $id       = $rHash{$curBlock};
                my $blockRem = $obj->block($id);
                $obj->remove_block($blockRem);
                delete $blockName{$id};
                $curBlock = "";
                $blockDrop->configure( -choices => \%blockName );
                $blockDrop->update;
                $blockDrop->bell;
                $blockMessage->configure( -text => "Block Removed" );
                refresh_section( $tree, $obj, $path, 1 );
                set_dirty();
                $change = 1;
            }
        }
    )->grid( -column => 3, -row => 2, -sticky => 'nsew' );

    $blockEdit = $top->Button(
        -text    => "Edit Block",
        -command => sub {
            if ( $curBlock ne "" ) {
                my %rHash     = reverse %blockName;
                my $id        = $rHash{$curBlock};
                my $blockEdit = $obj->block($id);
                my $answer    = _edit_block_dialog( $top, $tree, $blockEdit,
                                           $path . "/Block" . $blockEdit->id );
                if ($answer) {
                    $blockMessage->configure( -text => "Block Changed" )
                      if $answer == 1;
                    $blockMessage->configure( -text => "Block Removed" )
                      if $answer == 2;
                    $curBlock = "" if $answer == 2;
                    $top->bell;
                    my @teach2 = $obj->teachers;
                    my %teachName2;
                    foreach my $i (@teach2) {
                        $teachName2{ $i->id } =
                          $i->firstname . " " . $i->lastname;
                    }
                    @teachersO    = @teach2;
                    %teacherNameO = %teachName2;
                    $teachDropO->configure( -choices => \%teacherNameO );
                    $teachDropO->update;
                    if ( $answer == 2 ) {
                        delete $blockName{$id};
                        $blockDrop->configure( -choices => \%blockName );
                        $blockDrop->update;
                    }
                    $change = 1;
                }
                else {
                    $blockMessage->configure( -text => "" );
                }
            }
        }
    )->grid( -column => 2, -row => 2, -sticky => 'nsew' );

    $blockMessage =
      $top->Label( -text => "" )
      ->grid( -column => 1, -row => 3, -sticky => 'nsew' );

    $top->Label( -text => "" )->grid( -columnspan => 4 );

    #--------------------------------------------------------
    # Teacher Add/REmove
    #--------------------------------------------------------

    $teachDropN = $top->JBrowseEntry(
                                      -variable => \$curTeachN,
                                      -state    => 'readonly',
                                      -choices  => \%teacherNameN,
                                      -width    => 12
                                    );

    my $teachDropNEntry = $teachDropN->Subwidget("entry");
    $teachDropNEntry->configure( -disabledbackground => "white" );
    $teachDropNEntry->configure( -disabledforeground => "black" );

    $teachDropO = $top->JBrowseEntry(
                                      -variable => \$curTeachO,
                                      -state    => 'readonly',
                                      -choices  => \%teacherNameO,
                                      -width    => 12
                                    );

    my $teachDropOEntry = $teachDropO->Subwidget("entry");
    $teachDropOEntry->configure( -disabledbackground => "white" );
    $teachDropOEntry->configure( -disabledforeground => "black" );

    $teachAdd = $top->Button(
        -text    => "Set to all blocks",
        -command => sub {
            if ( $curTeachN ne "" ) {
                my %rHash    = reverse %teacherNameN;
                my $id       = $rHash{$curTeachN};
                my $teachAdd = $Schedule->teachers->get($id);
                $obj->assign_teacher($teachAdd);
                $teacherNameO{$id} =
                  $teachAdd->firstname . " " . $teachAdd->lastname;
                $curTeachN = "";
                $teachDropO->configure( -choices => \%teacherNameO );
                $teachDropO->update;
                $teachMessage->configure( -text => "Teacher Added" );
                $teachMessage->update;
                $teachMessage->bell;
                refresh_section( $tree, $obj, $path, 1 );
                $change = 1;
            }
        }
    );

    $teachTextN = $top->Label(
                               -text   => "Add Teacher: ",
                               -anchor => 'w'
                             )->grid( $teachDropN, '-', $teachAdd, -sticky => 'nsew' );

    $teachRem = $top->Button(
        -text    => "Remove from all blocks",
        -command => sub {
            if ( $curTeachO ne "" ) {
                my %rHash    = reverse %teacherNameO;
                my $id       = $rHash{$curTeachO};
                my $teachRem = $Schedule->teachers->get($id);
                $obj->remove_teacher($teachRem);
                $curTeachO = "";
                delete $teacherNameO{$id};
                $teachDropO->configure( -choices => \%teacherNameO );
                $teachDropO->update;
                $teachMessage->configure( -text => "Teacher Removed" );
                $teachMessage->bell;
                $teachMessage->update;
                $change = 1;
                refresh_section( $tree, $obj, $path, 1 );
            }
        }
    );

    $teachTextO = $top->Label(
                               -text   => "Remove Teacher: ",
                               -anchor => 'w'
                             )->grid( $teachDropO, '-', $teachRem, -sticky => 'nsew' );

    $teachMessage = $top->Label( -text => "" )->grid( -columnspan => 4 );

    #--------------------------------------------------------
    # Stream Add/REmove
    #--------------------------------------------------------

    $streamDropN = $top->JBrowseEntry(
                                       -variable => \$curStreamN,
                                       -state    => 'readonly',
                                       -choices  => \%streamNameN,
                                       -width    => 12
                                     );

    my $streamDropNEntry = $streamDropN->Subwidget("entry");
    $streamDropNEntry->configure( -disabledbackground => "white" );
    $streamDropNEntry->configure( -disabledforeground => "black" );

    $streamDropO = $top->JBrowseEntry(
                                       -variable => \$curStreamO,
                                       -state    => 'readonly',
                                       -choices  => \%streamNameO,
                                       -width    => 12
                                     );

    my $streamDropOEntry = $streamDropO->Subwidget("entry");
    $streamDropOEntry->configure( -disabledbackground => "white" );
    $streamDropOEntry->configure( -disabledforeground => "black" );

    $streamAdd = $top->Button(
        -text    => "Set Stream",
        -command => sub {
            if ( $curStreamN ne "" ) {
                $change = 1;
                my %rHash     = reverse %streamNameN;
                my $id        = $rHash{$curStreamN};
                my $streamAdd = $Schedule->streams->get($id);
                $obj->assign_stream($streamAdd);
                $streamNameO{$id} =
                  $streamAdd->number . ": " . $streamAdd->descr;
                $curStreamN = "";
                $streamDropO->configure( -choices => \%streamNameO );
                $streamDropO->update;
                $streamMessage->configure( -text => "Stream Set" );
                $streamMessage->update;
                $streamMessage->bell;
                refresh_schedule($tree);
            }
        }
    );

    $streamTextN = $top->Label(
                                -text   => "Add Stream: ",
                                -anchor => 'w'
                              )->grid( $streamDropN, '-', $streamAdd, -sticky => 'nsew' );

    $streamRem = $top->Button(
        -text    => "Remove Stream",
        -command => sub {
            if ( $curStreamO ne "" ) {
                $change = 1;
                my %rHash     = reverse %streamNameO;
                my $id        = $rHash{$curStreamO};
                my $streamRem = $Schedule->streams->get($id);
                $obj->remove_stream($streamRem);
                delete $streamNameO{$id};
                $curStreamO = "";
                $streamDropO->configure( -choices => \%streamNameO );
                $streamDropO->update;
                $streamMessage->configure( -text => "Stream Removed" );
                $streamMessage->update;
                $streamMessage->bell;
                refresh_schedule($tree);
            }
        }
    );

    $streamTextO = $top->Label(
                                -text   => "Remove Stream: ",
                                -anchor => 'w'
                              )->grid( $streamDropO, '-', $streamRem, -sticky => 'nsew' );

    $streamMessage =
      $top->Label( -text => "" )->grid( -columnspan => 4, -sticky => 'n' );

    my ( $columns, $rows ) = $top->gridSize();
    for ( my $i = 1 ; $i < $columns ; $i++ ) {
        $top->gridColumnconfigure( $i, -weight => 1 );
    }
    $top->gridRowconfigure( $rows - 1, -weight => 1 );

    $edit_dialog->configure( -focus => $blockDrop );

    my $answer = $edit_dialog->Show();
    $answer = "NO" unless $answer;

    if ( $answer eq 'Delete' ) {

        my $sure = $frame->DialogBox( -title   => "Delete?",
                                      -buttons => [ 'Yes', 'NO' ] );

        $sure->Label( -text => "Are you Sure You\nWant To Delete?" )->pack;

        my $answer2 = $sure->Show();

        return _edit_section_dialog( $frame, $tree, $obj, $path )
          if ( $answer2 eq 'NO' );

        $objPar->remove_section($obj);
        refresh_course( $tree, $objPar, $parent, 1 );
        set_dirty();
        return 2;
    }
    else {
        if ( $oldName ne $cName || $hoursN != $hoursO) {
            $obj->name($cName);
            $obj->hours($hoursN);
            refresh_schedule($tree);
            set_dirty();
        }
        else {
            set_dirty() if $change;
            return $change;
        }
    }
}

