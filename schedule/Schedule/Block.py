from Time_slot import TimeSlot
from Conflict import Conflict


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

