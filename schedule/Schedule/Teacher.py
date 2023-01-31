class TeacherMeta(type):
    """Metaclass for Teacher, making it iterable."""
    _instances = {}

    def __iter__(self):
        return iter(getattr(self, '_instances'))

    # =================================================================
    # share_blocks
    # =================================================================

    def share_blocks(self, block1, block2):
        """Checks if there are teachers who share these two blocks."""
        # Count occurrences in both sets to ensure that all values are < 2
        occurrences: dict[int, int] = {}

        # Get all the teachers in the first and second sets.
        for teacher in block1.teachers():
            if teacher.id not in occurrences.keys():
                occurrences[teacher.id] = 0
            occurrences[teacher.id] += 1

        for teacher in block2.teachers():
            if teacher.id not in occurrences.keys():
                occurrences[teacher.id] = 0
            occurrences[teacher.id] += 1

        # A count of 2 means the teachers are in both sets.
        for count in occurrences.values():
            if count >= 2:
                return True

        return False

    # =================================================================
    # add
    # =================================================================
    def add(self, *args):
        """Adds a new Teacher to the Teachers object.
        
        Returns the Teachers object."""
        for teacher in args:
            if not isinstance(teacher, Teacher):
                raise TypeError(f"<{teacher}>: invalid teacher - must be a Teacher object.")
            self._instances[teacher.id] = teacher
        return self

    # =================================================================
    # get
    # =================================================================
    def get(self, teacher_id: int):
        """Returns the Teacher object matching the passed ID, if it exists."""
        for teacher in self._instances.values():
            if teacher.id == teacher_id:
                return teacher
        return None

    # =================================================================
    # get_by_name
    # =================================================================
    def get_by_name(self, first_name: str, last_name: str):
        """Returns the first Teacher found matching the first name and last name, if one exists."""
        if not (first_name and last_name):
            return None
        for teacher in self._instances:
            if teacher.firstname == first_name and teacher.lastname == last_name:
                return teacher
        return None

    # =================================================================
    # remove teacher 
    # =================================================================
    def remove(self, teacher):
        """Removes this Teacher from the Teachers object.
        
        Returns the modified Teachers object."""
        if not isinstance(teacher, Teacher):
            raise TypeError(f"<{teacher}>: invalid teacher - must be a Teacher object.")
        if self._instances[teacher.id]:
            del self._instances[teacher.id]

        return self

    # =================================================================
    # list 
    # =================================================================
    def list(self):
        """Returns an array of Teacher objects."""
        return list(self._instances.values())

    # =================================================================
    # disjoint 
    # =================================================================
    def disjoint(self, rhs):
        """Determine if the current set of teachers is disjoint with the provided set of teachers."""
        occurrences = {}

        # Get all the teachers in the current set.
        for teacher in self.list():
            if teacher.id not in self._instances.keys():
                occurrences[teacher.id] = 0
            occurrences[teacher.id] += 1

        # Get all the teachers in the provided set.
        for teacher in rhs.list():
            if teacher.id not in self._instances.keys():
                occurrences[teacher.id] = 0
            occurrences[teacher.id] += 1

        # A teacher count of 2 means they're in both sets.
        for count in occurrences.values():
            if count >= 2:
                return False

        return True


# SYNOPSIS

#    use Schedule::Teacher;

#    my $teacher = Teacher->new (-firstname => $name, 
#                                -lastname => $lname,
#                                -dept     => $dept
#                               );


class Teacher(metaclass=TeacherMeta):
    _max_id = 0

    """Describes a teacher."""

    # -------------------------------------------------------------------
    # new
    # --------------------------------------------------------------------

    def __init__(self, firstname: str, lastname: str, dept: str = "", **kwargs):
        """Creates a Teacher object.
        
        Parameter firstname: str -> first name of the teacher.
        Parameter lastname: str -> last name of the teacher.
        Parameter dept -> department that this teacher is associated with (optional)"""
        self.firstname = firstname
        self.lastname = lastname
        self.dept = dept
        Teacher._max_id += 1
        self.__id = Teacher._max_id
        self.release = 0

        # keep **kwargs and below code, allows YAML to work correctly (kwargs should be last param)
        for k, v in kwargs.items():
            try:
                if hasattr(self, f"__{k}"):
                    setattr(self, f"__{k}", v)
                elif hasattr(self, f"_{k}"):
                    setattr(self, f"_{k}", v)
                elif hasattr(self, f"{k}"):
                    setattr(self, f"{k}", v)
                # if k == "id": Teacher._max_id -= 1
            except AttributeError:
                continue  # hit get-only property

    # =================================================================
    # id
    # =================================================================

    @property
    def id(self):
        """Returns the unique ID for this Teacher."""
        return self.__id

    # =================================================================
    # firstname
    # =================================================================
    @property
    def firstname(self):
        """Gets and sets the Teacher's name."""
        return self.__firstname

    @firstname.setter
    def firstname(self, new_name: str):
        if not (new_name and not new_name.isspace()):
            raise Exception("First name cannot be an empty string")

        self.__firstname = new_name

    # =================================================================
    # lastname
    # =================================================================
    @property
    def lastname(self):
        """Gets and sets the Teacher's last name."""
        return self.__lastname

    @lastname.setter
    def lastname(self, new_name: str):
        if not (new_name and not new_name.isspace()):
            raise Exception("Last name cannot be an empty string")
        self.__lastname = new_name

    # =================================================================
    # dept
    # =================================================================
    # NOTE: May or may not remove these due to it being not Pythonic to have such simple getters/setters.
    @property
    def dept(self):
        """Gets and sets the name of the Teacher's department."""
        return self.__dept

    @dept.setter
    def dept(self, new_dept: str):
        self.__dept = new_dept

    # =================================================================
    # release
    # =================================================================
    @property
    def release(self):
        """How much release time does the teacher have (per week) from teaching duties?"""
        return self._release

    @release.setter
    def release(self, new_rel: float):
        self._release = new_rel

    # =================================================================
    # print_description
    # =================================================================
    def print_description(self):
        """Returns a text string that describes the Teacher."""

        return f"{self.firstname} {self.lastname}"
