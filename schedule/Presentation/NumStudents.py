from __future__ import annotations
import sys
from os import path

sys.path.append(path.dirname(path.dirname(__file__)))
import GUI.NumStudentsTk as gui_form
import globals
import Schedule.Schedule as sched


# TODO: Change the status bar to be able to include two files
# TODO: Fall/Winter sub-Notebooks

class NumStudents:
    """NumStudents - provides methods / objects for entering number of students per course per section"""

    def __init__(self, frame, schedules: [sched.Schedule]):
        """
        Gathers data to present to the NumStudents gui form

        Inputs
        ------
        frame - a gui frame which will be the container object for the new form
        schedules - dictionary
                  - Key = semester name, value = schedule object
        """
        self.frame = frame
        self.refresh(schedules)

    def refresh(self, schedules: [sched.Schedule]):
        """
        Re-draw the student numbers for semesters/courses/section

        Inputs
        ------
        schedules - dictionary
                  - Key = semester name, value = schedule object
        """

        data = gui_form.NumStudentsData()
        for semester_name in ("fall", "winter", "summer"):
            if semester_name not in schedules.keys(): continue
            semester = gui_form.NumStudentsDataSemester(name=semester_name)
            data.semesters.append(semester)

            courses =

#            my @ courses =            grep { $_->needs_allocation} $schedule->all_courses();

            for course_name in ():

            schedule = schedules[semester_name]

"""    data = NumStudentsData()
    for semester_name in ("fall", "winter"):
        semester = NumStudentsDataSemester(name=semester_name)
        data.semesters.append(semester)
        for course_name in ("abc", "def", "ghi", "jkl"):
            course = NumStudentsDataCourse(name=course_name)
            semester.courses.append(course)
            for section_name in ("1", "2"):
                section = NumStudentsDataSection(name=section_name, num_students=10)
                section.data_validate = validate_factory(data, section)
                course.sections.append(section)
"""


"""

{

# from this we can infer that there are multiple schedulers, one for each semester
% Schedules = (% $schedule_ref);
my @ semesters = (sort keys % Schedules);

$Gui = NumStudentsTk->new( $self->{-frame}, \

@semesters

);
my % sections = ();

# @student_info:
# array [
#       hash { -semester=semester_name,
#              -course = hash {
#                   short_description -> hash {
#                                           section_number => hash {
#                                                                   -student_number => number
#                                                                   -validate=>validate_method
#                                                                   }
#                                           }
#                               }
my @ student_info;

foreach
my $semester( @ semesters) {
    my $schedule = $Schedules
{$semester};

my $info_by_semester = {-semester = > $semester, -courses = > {}};
push @ student_info,$info_by_semester;

my @ courses =
grep
{ $_->needs_allocation} $schedule->all_courses();

my $row = 0;
foreach
my $course( @ courses) {

$info_by_semester->{-courses}
->{ $course->short_description} = {};

foreach
my $section(sort
{ $a->number
cmp $b->number}
$course->sections )
{
    my $student_number = $section->num_students;
$info_by_semester->{-courses}
->{ $course->short_description}
->{ $section->number} = {
    -student_number = >  \$student_number,
-validate_sub = > [ \ & validate, $section]

};
}
}
}
$Gui->refresh(\

@student_info

);
}

# =================================================================
# validate that number be entered in a entry box is a real number
# (positive real number)
# =================================================================
sub
validate
{
no
warnings;
my $section = shift;
my $n = shift;
$n = 0
unless $n;
if ($n =~ / ^ (\s * \d * \s *)$ / ) {
$section->num_students($n);
$$Dirty_ptr = 1;
return 1;
}
return 0;
}

1;
"""
