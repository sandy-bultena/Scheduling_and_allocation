#!/usr/bin/perl
use strict;
use warnings;

package FontsAndColoursTk;
use FindBin;
use lib "$FindBin::Bin/../";
use Tk;
use Tk::InitGui;
use PerlLib::Colours;



my $Colours;
my $Fonts;

sub setup {
    my $class = shift;
    my $mw = shift;

    # Gets and sets the colours and fonts
    ( $Colours, $Fonts ) = InitGui->set($mw);

    # Hard code the colours
    $Colours = {
                 WorkspaceColour           => "#eeeeee",
                 WindowForeground          => "black",
                 SelectedBackground        => "#cdefff",
                 SelectedForeground        => "#0000ff",
                 DarkBackground            => "#cccccc",
                 ButtonBackground          => "#abcdef",
                 ButtonForeground          => "black",
                 ActiveBackground          => "#89abcd",
                 highlightbackground       => "#0000ff",
                 ButtonHighlightBackground => "#ff0000",
                 DataBackground            => "white",
                 DataForeground            => "black",
    };

    SetSystemColours( $mw, $Colours );
    $mw->configure( -bg => $Colours->{WorkspaceColour} );
    
}

sub Colours {
    my $class = shift;
    return $Colours;
}

sub Fonts {
    my $class = shift;
    return $Fonts;
}

1;
