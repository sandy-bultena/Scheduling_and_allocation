import re
from warnings import warn
# from Section import Section
from .Stream import Stream
from .Teacher import Teacher
from .Lab import Lab


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

    # =================================================================
    # add
    # =================================================================
    def add(self, course):
        
        if not isinstance(course, Course):
            raise TypeError(f"<{course}>: invalid course - must be a Course object")
        self._instances[course.id] = course



class Course(metaclass=CourseMeta):
    # ideally iterable is implemented with dict; if not, yaml write needs to be modified accordingly
    _max_id = 0

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------
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

    # =================================================================
    # number
    # =================================================================
    @property
    def number(self):
        """Gets and sets the Course number."""
        return self.__number

    @number.setter
    def number(self, new_num):
        self.__number = new_num

    # =================================================================
    # add_ section
    # =================================================================
    def add_section(self, *sections):
        """Assign a Section to this Course.
        
        Returns the modified Course object."""
        if not hasattr(self, '_sections'):
            self._sections = {}

        # In Perl, this function is structured in a way that allows it to take multiple sections and add them all to
        # the Course, one at a time. However, it is never actually used that way. I am preserving the original
        # structure just in case.
        for section in sections:
            # Verify that this is actually a Section object. NOTE: the Section import has been taken out to avoid a circular dependency.
            if not isinstance(section, object):
                raise TypeError(f"<{section}>: invalid section - must be a Section object.")

            # -------------------------------------------------------
            # Section numbers must be unique for this Course.
            # -------------------------------------------------------
            duplicate = False
            for sec in self._sections.values():
                if section.number == sec.number:
                    duplicate = True
                    break
            if duplicate:
                raise Exception(f"<{section.number}>: section number is not unique for this Course.")

            # ----------------------------------------------------------
            # save section for this course, save course for this section
            # ----------------------------------------------------------
            self._sections[section.number] = section
            section.course = self

        return self

    # =================================================================
    # get_section
    # =================================================================
    def get_section(self, number):
        """Gets the Section from this Course that has the passed section number, if it exists. Otherwise,
        returns None. """
        if hasattr(self, '_sections') and number in self._sections.keys():
            return self._sections[number]
        return None

    # =================================================================
    # get_section_by_id
    # =================================================================
    def get_section_by_id(self, sect_id):
        """Gets the Section from this Course that matches the passed section ID, if it exists.
        
        Returns the Section if found, or None otherwise."""
        if hasattr(self, '_sections'):
            sections = self.sections()
            for i in sections:
                if i.id == sect_id:
                    return i

        return None

    # =================================================================
    # get_section_by_name
    # =================================================================
    def get_section_by_name(self, name: str):
        """Gets the Section from this Course that has the passed section name, if it exists.
        
        Returns a list containing the Section if found, or an empty list otherwise."""
        # NOTE: This method is coded to return an array in the Perl code. However, the one place where this function
        # is being called--AssignToResource.pm--only cares about the first element of the returned array.
        # I'm keeping the structure as-is, but this will probably need revision.
        to_return = []
        if name:
            sections = self.sections()
            for i in sections:
                if i.name == name:
                    to_return.append(i)
        return to_return

    # =================================================================
    # remove_section
    # =================================================================
    def remove_section(self, section):
        """Removes the passed Section from this Course, if it exists.
        
        Returns the modified Course object."""
        # Verify that the section is indeed a Section object. NOTE: the Section import has been taken out to avoid a circular dependency.
        if not isinstance(section, object):
            raise TypeError(f"<{section}>: invalid section - must be a Section object")

        if hasattr(self, '_sections') and section.number in getattr(self, '_sections', {}):
            del self._sections[section.number]

        section.delete()

        return self

    # =================================================================
    # delete
    # =================================================================
    def delete(self):
        """Delete this object (and all its dependants).
        
        Returns None."""
        for section in self.sections():
            self.remove_section(section)
        # TODO: Remove this Course from the CourseMeta's instances.

    # =================================================================
    # sections
    # =================================================================
    def sections(self):
        """Returns a list of all the Sections assigned to this Course."""
        return list(getattr(self, '_sections', {}).values())

    # =================================================================
    # number of sections
    # =================================================================
    def number_of_sections(self):
        """Returns the number of Sections assigned to this Course."""
        sections = self.sections()
        return len(sections)

    # =================================================================
    # sections for teacher
    # =================================================================
    def sections_for_teacher(self, teacher):
        """Returns a list of the Sections assigned to this course, with this Teacher."""
        sections = []

        for section in self.sections():
            for teacher_id in section.teachers():
                if teacher.id == teacher_id:
                    sections.append(section)

        return sections

    # =================================================================
    # max_section_number
    # =================================================================
    def max_section_number(self):
        """Returns the maximum Section number from the Sections assigned to this Course."""
        sections = sorted(self.sections(), key=lambda s: s.number)
        return sections[-1].number if len(sections) > 0 else 0

    # =================================================================
    # blocks
    # =================================================================
    def blocks(self):
        """Returns a list of the Blocks assigned to this Course."""
        blocks = []

        for section in self.sections():
            blocks.append(section.blocks)

        return blocks

    # =================================================================
    # section
    # =================================================================
    def section(self, section_number):
        """Returns the Section associated with this Section number."""
        if hasattr(self, '_sections'):
            return self._sections[section_number]

    # =================================================================
    # print_description
    # =================================================================
    def print_description(self):
        """Returns a text string that describes the Course, its Sections, its Blocks, its Teachers, and its Labs."""
        text = ''

        # Header
        text += "\n\n"
        text += '=' * 50 + "\n"

        # Sections
        for s in sorted(self.sections(), key=lambda x: x.number):
            text += f"\n{s}\n"
            text += "-" * 50 + "\n"

            # Blocks
            for b in s.blocks.sort(key=lambda x: x.day_number or x.start_number):
                text += f"{b.day} {b.start}, {b.duration} hours\n"
                text += "\tlabs: " + ", ".join(b.labs()) + "\n"
                text += "\tteachers: "
                text += ", ".join(b.teachers())
                text += "\n"

        return text

    # =================================================================
    # print_description2
    # =================================================================
    def print_description2(self):
        """Returns a brief string containing the Course's number and name, in the format 'Number: Name'."""
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.number}: {self.name}"

    # =================================================================
    # teachers
    # =================================================================
    def teachers(self):
        """Returns a list of the Teachers assigned to all Sections of this Course."""
        teachers = {}

        for section in self.sections():
            for teacher in section.teachers():
                teachers[teacher] = teacher

        return list(teachers.values())

    # =================================================================
    # has teacher
    # =================================================================
    def has_teacher(self, teacher: Teacher):
        """Returns true if the passed Teacher is assigned to this Course."""
        if not teacher:
            return False

        for t in self.teachers():
            if t.id == teacher.id:
                return True
        return False

    # =================================================================
    # streams
    # =================================================================
    def streams(self):
        """Returns a list of Streams assigned to all Sections of this Course."""
        streams = {}

        for section in self.sections():
            for stream in section.streams():
                streams[stream] = stream

        return list(streams.values())

    # =================================================================
    # has_stream
    # =================================================================
    def has_stream(self, stream):
        """Returns true if this Course has the specified Stream."""
        if not stream:
            return False

        for s in self.streams():
            if s.id == stream.id:
                return True

        return False

    # =================================================================
    # assign_teacher
    # =================================================================
    def assign_teacher(self, teacher: Teacher):
        """Assigns a Teacher to all Sections of this Course.
        
        Returns the modified Course object."""
        if teacher:
            for section in self.sections():
                section.assign_teacher(teacher)

        return self

    # =================================================================
    # assign_lab
    # =================================================================
    def assign_lab(self, lab: Lab):
        """Assigns a Lab to all Sections of this Course.
        
        Returns the modified Course object."""
        if lab:
            for section in self.sections():
                section.assign_lab(lab)

        return self

    # =================================================================
    # assign_stream
    # =================================================================
    def assign_stream(self, stream: Stream):
        """Assigns a Stream to all Sections of this Course.
        
        Returns the modified Course object."""
        if stream:
            for section in self.sections():
                section.assign_stream(stream)

        return self

    # =================================================================
    # remove_teacher
    # =================================================================
    def remove_teacher(self, teacher: Teacher):
        """Removes the passed Teacher from all Blocks in this Course.
        
        Returns the modified Course object."""
        for section in self.sections():
            section.remove_teacher(teacher)

        return self

    # =================================================================
    # remove_all_teachers
    # =================================================================
    def remove_all_teachers(self):
        """Removes all Teachers from all Blocks in this Course.
        
        Returns the modified Course object."""
        for teacher in self.teachers():
            self.remove_teacher(teacher)

        return self

    # =================================================================
    # remove_stream
    # =================================================================
    def remove_stream(self, stream):
        """Removes the specified Stream from this Course.
        
        Returns the modified Course object."""
        for section in self.sections():
            section.remove_stream(stream)

        return self

    # =================================================================
    # remove_all_streams
    # =================================================================
    def remove_all_streams(self):
        """Removes all Streams from all Sections of this Course.
        
        Returns the modified Course object."""
        for stream in self.streams():
            self.remove_stream(stream)

        return self

    # =======================================
    # Get unused section number (Alex Code)
    # =======================================
    def get_new_number(self, number: int):
        """Returns the first unused Section Number."""
        while self.get_section(number):
            number += 1
        return number
