from Lab import Lab
from Section import Section
from Teacher import Teacher
from Time_slot import TimeSlot, TimeSlotMeta


class BlockMeta(TimeSlotMeta):
    """Metaclass for Block, making it iterable."""
    _instances = []

    # =================================================================
    # get_day_blocks ($day, $blocks)
    # =================================================================
    def get_day_blocks(self, day, blocks: list):
        """Returns an array of all blocks within a specific day.
        
        Parameter day: int -> day of the week (1=monday, 2=tuesday, etc.)
        Parameter blocks: list -> An array of AssignBlocks."""
        if not blocks:
            return []
        day_blocks = filter(lambda x: x.day == day, blocks)
        return list(day_blocks)


# SYNOPSIS:

#    use Schedule::Course;
#    use Schedule::Section;
#    use Schedule::Block;

#    my $block = Block->new (-day=>"Wed",-start=>"9:30",-duration=>1.5);

#    my $course = Course->new(-name=>"Basket Weaving");
#    my $section = $course->create_section(-section_number=>1);
#    $section->add_block($block);                                   section.add_block(block)

#    print "block belongs to section ",$block->section;     // print(f"block belongs to section {block.section}")

#    $block->assign_teacher($teacher);  //  block.assign_teacher(teacher)
#    $block->remove_teacher($teacher);      block.remove_teacher(teacher)
#    $block->teachers();                    block.teachers()

#    $block->add_lab("P327");               block.add_lab("P327")
#    $block->remove_lab("P325");            block.remove_lab("P325")
#    $block->labs();                        block.labs()


class Block(TimeSlot, metaclass=BlockMeta):
    """
    Describes a block which is a specific time slot for teaching part of a section of a course.
    """

    # =================================================================
    # Class Variables
    # =================================================================

    _max_id = 0
    _DEFAULT_DAY = 'mon'

    # =================================================================
    # Constructor
    # =================================================================

    def __init__(self, day: str, start: str, duration: float, number: int) -> None:
        """Creates a new Block object.
        
        - Parameter day: str -> 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'
        - Parameter start: str -> start time using 24 h clock (i.e 1pm is "13:00")
        - Parameter duration: float -> how long does this class last, in hours
        - Parameter number: int -> A number representing this specific Block.
        """
        super().__init__(day, start, duration)
        self.number = number  # NOTE: Based on the code found in CSV.pm and Section.pm
        Block._max_id += 1
        self._block_id = Block._max_id
        Block._instances.append(self)
        self.__section = None

    # =================================================================
    # number
    # =================================================================

    @property
    def number(self):
        """Gets and sets the Block number."""
        return self.__number

    @number.setter
    def number(self, new_num: int):
        # NOTE: The reason it checks for strings in the Perl code is because Perl doesn't distinguish between strings
        # and numbers: A value of "0" registers as 0, and vice versa.
        if new_num is None or not isinstance(new_num, int):
            raise Exception(f"<{new_num}>: section number must be an integer and cannot be null.")
        self.__number = new_num

    # =================================================================
    # delete
    # =================================================================
    def delete(self):
        """Delete this Block object and all its dependents."""
        # self = None  # TODO: Verify that this works as intended. NOTE: It does not. del self  # NOTE: Neither does
        #  this. NOTE: So far as I can tell, the only place this method is being called is in Section's remove_block(
        #  ) method, to destroy the reference to a local Block parameter after said Block has already been removed
        #  from Section's array/hash of Blocks. Because of this, and because it doesn't seem possible to make an
        #  object delete itself in Python, I don't believe that this method is needed.
        Block._instances.remove(self)
        self = None

    # =================================================================
    # start
    # =================================================================
    @property
    def start(self):
        """Get/set the start time of the Block, in 24hr clock."""
        return super().start

    @start.setter
    def start(self, new_start: str):
        super(Block, self.__class__).start.fset(self, new_start)

        # If there are synchronized blocks, we must change them too.
        # Beware infinite loops!
        for other in self.synced():
            old = other.start
            if old != super().start:
                other.start = super().start # Attempting to directly write to the backing field doesn't work.
                # Fortunately, calling the property like this doesn't result in an infinite loop.

    # =================================================================
    # day
    # =================================================================
    @property
    def day(self):
        """Get/set the day of the block, in numeric format (1 for Monday, 7 for Sunday)."""
        return super().day

    @day.setter
    def day(self, new_day):
        super(Block, self.__class__).day.fset(self, new_day)

        # If there are synchronized blocks, change them too.
        # Once again, beware the infinite loop!
        for other in self.synced():
            old = other.day
            if old != super().day:
                other.day = super().day

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
    def section(self, section: Section):
        if isinstance(section, Section):
            self.__section = section
        else:
            raise TypeError("<{section}>: invalid section - must be a Section object.")

    # =================================================================
    # assign_lab
    # =================================================================
    def assign_lab(self, lab: Lab):
        """Assign a lab to this block."""

        # If the Block doesn't already have a labs dict, create one.
        if not hasattr(self, '_labs'):
            self._labs = {}

        if not isinstance(lab, Lab):
            raise TypeError(f"<{lab}>: invalid lab - must be a Lab object.")

        # TODO: Check if this function allows multiple labs to be assigned at once in the perl version
        self._labs[lab.id] = lab

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
            raise TypeError(f"<{lab}>: invalid lab - must be a Lab object.")

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
        for lab in list(self._labs.values()):
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

    # =================================================================
    # has_lab
    # =================================================================
    def has_lab(self, lab: Lab):
        """Returns true if the Block has the specified Lab."""
        if not lab or not isinstance(lab, Lab):
            return False

        # If the Block doesn't already have a labs dict, create one.
        if not hasattr(self, '_labs'):
            self._labs = {}


        for key in self._labs:
            if self._labs[key].id == lab.id:
                return True

        return False

    # =================================================================
    # assign_teacher
    # =================================================================
    def assign_teacher(self, teacher):
        """Assigns a new teacher to this Block.
        
        Returns the Block object."""
        # If this Block doesn't already contain a Teachers dict, create one.
        if not hasattr(self, '_teachers'):
            self._teachers = {}

        # Verify that this teacher is, in fact, a Teacher. 
        if not isinstance(teacher, Teacher):
            raise TypeError(f"<{teacher}>: invalid teacher - must be a Teacher object.")

        self._teachers[teacher.id] = teacher

        return self

    # =================================================================
    # remove_teacher
    # =================================================================
    def remove_teacher(self, teacher):
        """Removes the specified Teacher from this Block.
        
        Returns the Block object."""
        # If this Block doesn't already contain a Teachers dict, create one.
        if not hasattr(self, '_teachers'):
            self._teachers = {}

        # Verify that the teacher is, in fact, a Teacher. 
        if not isinstance(teacher, Teacher):
            raise TypeError(f"<{teacher}>: invalid teacher - must be a Teacher object.")

        # If the teachers dict contains an entry for this Teacher, remove it.
        if teacher.id in self._teachers.keys():
            del self._teachers[teacher.id]

        return self

    # =================================================================
    # remove_all_teachers
    # =================================================================
    def remove_all_teachers(self):
        """Removes ALL teachers from this Block.
        
        Returns the Block object."""
        for teacher in self._teachers:
            self.remove_teacher(teacher)

        return self

    # =================================================================
    # teachers
    # =================================================================
    def teachers(self):
        """Returns a list of teachers assigned to this Block."""
        # If this Block doesn't already have a teachers dict, create one.
        if not hasattr(self, '_teachers'):
            self._teachers = {}
        return list(self._teachers.values())

    # =================================================================
    # has_teacher
    # =================================================================
    def has_teacher(self, teacher):
        """Returns True if this Block has the specified Teacher."""
        if not teacher:
            return False

        for key in self._teachers:
            if self._teachers[key].id == teacher.id:
                return True
        return False

    # =================================================================
    # teachersObj
    # =================================================================
    def teachersObj(self):
        """Returns a list of teacher objects to this Block."""
        # NOTE: Not entirely sure what this is meant to be doing in the original Perl.
        # ADDENDUM: There are no references to this method anywhere in the code beyond here. May get rid of it.
        return self._teachers

    # =================================================================
    # sync_block
    # =================================================================
    def sync_block(self, block):
        """The new Block object will be synced with this one 
        (i.e., changing the start time of this Block will change the start time of the synched block).
        
        Returns the Block object."""
        if not isinstance(block, Block):
            raise f"<{block}>: invalid block - must be a Block object."

        if not hasattr(self, '_sync'):
            self._sync = []
        self._sync.append(block)

        return self

    # =================================================================
    # unsync_block
    # =================================================================
    def unsync_block(self, block):
        """Removes syncing of Block from this Block.
        
        Returns this Block object."""

        # This function was not finished or used in the Perl code, so I'm flying blind here.
        if block in self._sync:
            self._sync.remove(block)

        return self

    # =================================================================
    # synced
    # =================================================================
    def synced(self):
        """Returns an array ref of the Blocks which are synced to this Block."""

        # If the sync array doesn't exist, create it.
        if not hasattr(self, '_sync'):
            self._sync = []

        return self._sync

    # =================================================================
    # reset_conflicted
    # =================================================================
    def reset_conflicted(self):
        """Resets conflicted field."""
        self._conflicted = False

    # =================================================================
    # conflicted
    # =================================================================
    @property
    def conflicted(self):
        """Gets and sets conflicted field."""
        if not hasattr(self, '_conflicted'):
            self._conflicted = False

        return self._conflicted

    @conflicted.setter
    def conflicted(self, new_conf: bool):
        if not hasattr(self, '_conflicted'):
            self._conflicted = False
        self._conflicted = bool(new_conf)

    # =================================================================
    # is_conflicted
    # =================================================================
    def is_conflicted(self):
        """Returns true if there is a conflict with this Block, false otherwise."""
        return self.conflicted

    # =================================================================
    # print_description
    # =================================================================
    def print_description(self):
        """Returns a text string that describes the Block.
        
        Includes information on any Section and Labs related to this Block."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns a text string that describes the Block.
        
        Includes information on any Section and Labs related to this Block."""
        text = ""

        if self.section:
            if self.section.course:
                text += self.section.course.name + " "
            text += f"{self.section.number} "

        text += f"{self.day} {self.start} for {self.duration} hours, in "
        # not intended result, but stops it from crashing
        text += ", ".join(str(l) for l in self._labs.values())

        return text

    def print_description_2(self):
        """Prints an alternate text string that describes this Block.
        
        Includes information which directly relates to this Block ONLY."""
        text = f"{self.number} : {self.day}, {self.start} {self.duration} hour(s)"
        return text

    # =================================================================
    # conflicts
    # =================================================================
    def conflicts(self):
        """Returns a list of the conflicts related to this Block."""
        if not hasattr(self, '_conflicts'):
            self._conflicts = []

        return self._conflicts

    # ===================================
    # Refresh Number
    # ===================================
    def refresh_number(self):
        """Assigns a number to a Block that doesn't have one."""
        # NOTE: Honestly not sure why this function is necessary.
        number = self.number
        section = self.section

        if number == 0:
            self.number = section.get_new_number()
        pass
