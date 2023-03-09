#!/usr/bin/perl
use strict;
use warnings;
use FindBin;    # find which directory this executable is in
use lib "$FindBin::Bin/";
use lib "$FindBin::Bin/Library";
our $BinDir = "$FindBin::Bin/";

use Presentation::Scheduler;

Scheduler::main();
