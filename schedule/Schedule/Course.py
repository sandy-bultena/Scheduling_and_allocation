# SYNOPSIS

#    use Schedule::Course;

#    my $block = Block->new (-day=>"Wed",-start=>"9:30",-duration=>1.5);
#    my $section = Section->new(-number=>1, -hours=>6);

#    my $course = Course->new(-name=>"Basket Weaving", -course_id="420-ABC-DEF");
#    $course->add_section($section);
#    $section->add_block($block);

#    print "Course consists of the following sections: ";
#    foreach my $section ($course->sections) {
# print info about $section
#    }


class CourseMeta(type):
    _instances = {}

    def __iter__(self):
        return iter(getattr(self, '_instances', {}))


class Course(metaclass=CourseMeta):
    # ideally iterable is implemented with dict; if not, yaml write needs to be modified accordingly
    _max_id = 0

    def __init__(self, **kwargs):
        self.name = "C"  # temp assignment to avoid crashes in Block __str__
