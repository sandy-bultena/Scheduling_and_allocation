from Time_slot import TimeSlot
from Conflict import Conflict
from Lab import Lab


# SYNOPSIS:

#    use Schedule::Course;
#    use Schedule::Section;
#    use Schedule::Block;

#    my $block = Block->new (-day=>"Wed",-start=>"9:30",-duration=>1.5);

#    my $course = Course->new(-name=>"Basket Weaving");
#    my $section = $course->create_section(-section_number=>1);
#    $section->add_block($block);

#    print "block belongs to section ",$block->section;

#    $block->assign_teacher($teacher);
#    $block->remove_teacher($teacher);
#    $block->teachers();

#    $block->add_lab("P327");
#    $block->remove_lab("P325");
#    $block->labs();


class Block(TimeSlot):
    """
    Describes a block which is a specific time slot for teaching part of a section of a course.
    """

    # =================================================================
    # Class Variables
    # =================================================================

    _max_id = 0
    _default_day = 'mon'

    # =================================================================
    # Constructor
    # =================================================================

    def __init__(self, day: str, start: str, duration: float, number) -> None:
        TimeSlot.__init__(self, day, start, duration)
        self.number = number
        Block._max_id += 1
        self._block_id = Block._max_id

    # =================================================================
    # number
    # =================================================================

    @property
    def number(self):
        """Gets and sets the Block number."""
        return self.__number

    @number.setter
    def number(self, new_num: str):
        if new_num is None or new_num == "":
            # TODO: Raise an exception. f"<{new_num}>: section number cannot be a null string.""
            pass
        self.__number = new_num

    # =================================================================
    # delete
    # =================================================================
    def delete(self):
        """Delete this Block object and all its dependents."""
        self = None  # TODO: Verify that this works as intended.

    # =================================================================
    # start
    # =================================================================
    @property
    def start(self):
        """Get/set the start time of the Block, in 24hr clock."""
        return super().start(self)

    @start.setter
    def start(self, new_start: str):
        super().start = new_start

        # If there are synchronized blocks, we must change them too.
        # Beware infinite loops!
        for other in self.synched:
            # TODO: Look into how to access superclass properties of another object in Python.
            old = super().start(other)
            if old != super().start(self):
                other.start = super().start(self)

    # =================================================================
    # day
    # =================================================================
    @property
    def day(self):
        """Get/set the day of the block, in numeric format (1 for Monday, 7 for Sunday)."""
        return super().day(self)

    @day.setter
    def day(self, new_day):
        super().day = new_day

        # If there are synchronized blocks, change them too.
        # Once again, beware the infinite loop!
        for other in self.synched:
            old = super().day(other)
            if old != super().day(self):
                other.day = super().day(self)

    # ==================================================================
    # id //ALEX CODE
    # ==================================================================

    @property
    def id(self):
        """Gets the Block id."""
        return self._block_id

    # =================================================================
    # section
    # =================================================================
    @property
    def section(self):
        """Gets and sets the course Section object which contains this Block."""
        return self.__section

    @section.setter
    def section(self, section):
        pass
        # # TODO: check whether this is a Section object. Section class must be written first.
        # if isinstance(section, Section):
        #     self.__section = section
        # else:
        #     raise f"<{section}>: invalid section - must be a Section object."

    # =================================================================
    # assign_lab
    # =================================================================
    def assign_lab(self, lab: Lab):
        """Assign a lab to this block."""

        # If the Block doesn't already have a labs dict, create one.
        if not hasattr(self, '_labs'):
            self._labs = {}

        if not isinstance(lab, Lab):
            raise f"<{lab}>: invalid lab - must be a Lab object."

        # TODO: Check if this function allows multiple labs to be assigned at once in the
        self._labs[lab.id] = lab
        # perl version.

        return self

    # =================================================================
    # remove_lab
    # =================================================================
    def remove_lab(self, lab: Lab):
        """Removes the specified Lab from this Block.

        Returns the Block object."""

        # If the Block doesn't already have a labs dict, create one.
        if not hasattr(self, '_labs'):
            self._labs = {}

        if not isinstance(lab, Lab):
            raise f"<{lab}>: invalid lab - must be a Lab object."

        # If the labs dict contains an entry for the specified Lab, remove it.
        if lab.id in self._labs.keys():
            del self._labs[lab.id]
        
        return self

    # =================================================================
    # remove_all_labs
    # =================================================================
    def remove_all_labs(self):
        """Removes ALL Labs from this Block.
        
        Returns the Block object."""
        for lab in self._labs:
            self.remove_lab(lab)

        return self

    # =================================================================
    # labs
    # =================================================================
    def labs(self):
        """Returns a list of the labs assigned to this block."""

        # If the Block doesn't already have a labs dict, create one.
        if not hasattr(self, '_labs'):
            self._labs = {}

        return list(self._labs.values())
