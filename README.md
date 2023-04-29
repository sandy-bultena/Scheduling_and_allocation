# SchedProg

A package of tools used for scheduling and allocating
teachers and labs etc.



Uses Perl/Tk GUI

Takes into account the following contraints
1. Teachers
2. Labs
3. Streams
4. Limits schedules based on current Collective Agreement Rules

Files are saved in YAML format, so they can be edited manually
if  you are brave enough.

## MAC OS X

### Install perl (this version used 5.30.3)
[perl](https://www.perl.org/get.html#osx)
(build from source, don't use ActivePerl)

### Install required Perl Packages

Assuming that you installed perl into /usr/local/bin...

```bash
sudo /usr/local/bin/cpan install YAML
sudo /usr/local/bin/cpan -fi Tk         # must force install Tk
sudo /usr/local/bin/cpan install Text::CSV
sudo /usr/local/bin/cpan install PDF::API2
```

### Install Scheduler and AllocationManager
Download zip file and unzip

From a terminal window (bash)

```bash
cd ../SchedProg/schedule/
/usr/local/bin/perl SchedulerManager.pl &
```

### Third Party Software

A X-windows emulator must be installed on your system.

Recommended: XQuartz

## MS Windows (Tested on Windows 10)

### Install Strawberry Perl

(version used .0.1-64bit - Newer versions available but have issues with Tk Package)
http://strawberryperl.com/release-notes/5.30.0.1-64bit.html


### Install required Perl Packages

Run Command Prompt as Administrator

```bash
cpan YAML
cpanm --Force Tk         # must force install Tk
cpan Text::CSV
cpan PDF::API2
```

## Alternative Installation

The above instructions assume that the software is being installed from the source on a clean machine, with no pre-existing Perl. It can alternatively be installed using a portable version of Strawberry Perl, with the required Perl packages already installed. In this context, the user works with a zipped folder containing Strawberry Perl portable, the application code, and a pair of batch scripts (one for each of the tools).

### INSTALLATION
To install the scheduler and allocation manager software on another computer, copy the folder containing these instructions onto a USB drive. Then copy it from the drive onto the computer you want to use it on.

### USE
To run the AllocationManager, double-click on the icon. To run the SchedulerManager, double-click on the icon. 


#### Python Packages needed
The following packages must be installed to run the Python version of the software:

- python-dotenv
- pony
- Pmw
