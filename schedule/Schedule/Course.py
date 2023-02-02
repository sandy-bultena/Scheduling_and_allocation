import re
from warnings import warn


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

    # -------------------------------------------------------------------
    # new
    #--------------------------------------------------------------------
    def __init__(self, number, name: str = "", semester: str = "", **kwargs):
        self.name = "C"  # temp assignment to avoid crashes in Block __str__
        Course._max_id += 1
        self.__id = Course._max_id
        self.number = number
        self.name = name
        self.semester = semester

    # =================================================================
    # id
    # =================================================================
    @property
    def id(self):
        """Returns the unique ID for this Course object."""
        return self.__id

    # =================================================================
    # name
    # =================================================================
    @property
    def name(self):
        """Gets or sets the Course name."""
        return self.__name

    @name.setter
    def name(self, new_name: str):
        self.__name = new_name

    # =================================================================
    # needs allocation
    # =================================================================
    @property
    def needs_allocation(self) -> bool:
        """Does this course need to be allocated (i.e., to have a teacher assigned)?
        
        For example, Math and Human Relations do not need to be allocated to one of our teachers.
        
        Defaults to true."""
        if not hasattr(self, '_allocation'):
            self._allocation = True
        return self._allocation

    @needs_allocation.setter
    def needs_allocation(self, allocation: bool):
        self._allocation = allocation

    # =================================================================
    # semester
    # =================================================================
    @property
    def semester(self):
        """Gets or sets the Course's semester (accepted values: 'summer', 'winter', 'fall', or blank)."""
        return self.__semester

    @semester.setter
    def semester(self, semester: str):
        semester = semester.lower()
        if not re.match("^(summer|winter|fall)"):
            warn(f"invalid semester for course; {semester}", Warning, stacklevel=2)
            semester = ""
        self.__semester = semester
    
    
