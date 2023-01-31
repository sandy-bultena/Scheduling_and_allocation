# SYNOPSIS

#    use Schedule::Teacher;
    
#    my $teacher = Teacher->new (-firstname => $name, 
#                                -lastname => $lname,
#                                -dept     => $dept
#                               );


class Teacher:
    _max_id = 0
    
    """Describes a teacher."""

    # -------------------------------------------------------------------
    # new
    #--------------------------------------------------------------------

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

        # keep **kwargs and below code, allows YAML to work correctly (kwargs should be last param)
        for k, v in kwargs.items():
            try:
                if hasattr(self, f"__{k}"): setattr(self, f"__{k}", v)
                elif hasattr(self, f"_{k}"): setattr(self, f"_{k}", v)
                elif hasattr(self, f"{k}"): setattr(self, f"{k}", v)
                #if k == "id": Teacher._max_id -= 1
            except AttributeError: continue # hit get-only property

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
        if not(new_name and not new_name.isspace()):
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
        if not(new_name and not new_name.isspace()):
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
