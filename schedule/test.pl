#!/usr/bin/perl;
use strict;
use warnings;
use Tie::Watch;

my $frog = 1;
my $func = sub {
    my $self = shift;
    print "Value is ",$frog,"\n";
    $self->Store();
   print "Value is ",$frog,"\n\n";
 };
 
 my $watch = Tie::Watch->new(
 -variable=>\$frog,
 -store=>$func);
 
 foreach my $i (0..10) {
     print "Enter number for frog: ";
     my $input = <>;
     chomp ($input);
     $frog = $input;
 }