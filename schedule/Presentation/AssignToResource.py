"""Create or assign Time Blocks to various resources."""
from ..GUI.AssignToResourceTk import AssignToResourceTk
from ..Schedule.Block import Block
from ..Schedule.Course import Course
from ..Schedule.Lab import Lab
from ..Schedule.Schedule import Schedule
from ..Schedule.Section import Section
from ..Schedule.Stream import Stream
from ..Schedule.Teacher import Teacher

# ===================================================================
# globals
# ===================================================================
global course
global section
global block
global teacher
global lab
global gui


class AssignToResource:
    """Create or assign Time Blocks to various resources.

    Called with a date/time/duration of a block, as well as a Teacher/Lab.

    Allows the user to assign this block to a Course and Section,
    or to create a new block.

    or to assign an existing block to Course and Section."""
    # =================================================================
    # Class/Global Variables
    # =================================================================
    global schedule
    global mw
    global Type
    Day_name = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday"
    }
    global Day
    global Start
    global Duration

    # ===================================================================
    # Constructor
    # ===================================================================
    def __init__(self, mw, schedule: Schedule, day: int, start, duration, schedulable):
        """Creates and manages a gui that will allow the user to assign a block to various
        resources.

        Parameters:
            mw: The main GUI window.
            schedule: Schedule object.
            day: new Block information
            start: new Block information
            duration: new Block information
            schedulable: Teacher or Lab (nothing will happen if this is a Stream object)."""
        global Day, Start, Duration
        Day = day
        Start = start
        Duration = duration

        global Type
        Type = schedule.get_view_type_of_object(schedulable)
        if Type == Lab:
            global lab
            lab = schedulable
        elif Type == Teacher:
            global teacher
            teacher = schedulable
        elif Type == Stream or Type is None:
            return

        # ------------------------------------
        # Create Dialog Box
        # ------------------------------------
        title = "Assign Block to " + Type
        block_text = f"{AssignToResource.Day_name[day]} at " \
                     f"{_hours_to_string(start)} for {duration} hour(s)"

        global gui
        gui = AssignToResourceTk(Type) # TODO: Implement this class.
        gui.draw(mw, title, block_text)

        # ------------------------------------
        # open dialog
        # ------------------------------------
        if schedule:
            AssignToResource._open_dialog()

    # ============================================================================
    # OpenDialog
    # ============================================================================
    def _open_dialog(self):
        # ------------------------------------
        # setup event handlers
        # ------------------------------------
        global gui
        gui: AssignToResourceTk

        # ------------------------------------
        # setup event handlers
        # ------------------------------------
        gui.cb_course_selected(AssignToResource._cb_course_selected)
        gui.cb_section_selected(_cb_section_selected)
        gui.cb_block_selected(_cb_block_selected)
        gui.cb_teacher_selected(_cb_teacher_selected)
        gui.cb_lab_selected(_cb_lab_selected)

        gui.cb_add_new_section(_cb_add_new_section)
        gui.cb_add_new_block(_cb_add_new_block)
        gui.cb_add_new_teacher(_cb_add_new_teacher)
        gui.cb_add_new_lab(_cb_add_new_lab)

        # ------------------------------------
        # get lists of resources
        # ------------------------------------

        # labs
        lab_names = {}
        global schedule
        schedule: Schedule
        for lab in schedule.labs():
            lab_names[lab.id] = str(lab)
        gui.set_lab_choices(lab_names)

        # teachers
        teacher_names = {}
        for teacher in schedule.teachers():
            teacher_names[teacher.id] = str(teacher)
        gui.set_teacher_choices(teacher_names)

        # courses
        course_names = {}
        for course in schedule.courses():
            course_names[course.id] = course.description
        gui.set_course_choices(course_names)

        # ------------------------------------
        # Show dialog
        # ------------------------------------
        answer = gui.show() or "Cancel"

        # ------------------------------------
        # assign block to resource
        # ------------------------------------
        if answer == "Ok":
            # check if a Block is defined.
            global block
            if block:
                block: Block
                # If it is, assign all properties to the Block.
                global Day, Start, Duration, lab, teacher
                block.day = Day
                block.start = _hours_to_string(Start)
                block.duration = Duration
                if lab:
                    block.assign_lab(lab)
                if teacher:
                    block.assign_teacher(teacher)
                return True
        return False

    # ============================================================================
    # callbacks
    # ============================================================================

    # ----------------------------------------------------------------------------
    # course was selected
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_course_selected(id: int):
        global course, schedule
        schedule: Schedule
        course: Course = Course.get(id)

        # since we have a new course, we need to nullify the sections and blocks.
        global section, block, gui
        section = None
        block = None
        gui: AssignToResourceTk
        gui.clear_sections_and_blocks()
        gui.enable_new_section_button()

        # What sections are available for this course?
        sections = course.sections()
        sections_dict = dict([(i.id, str(i)) for i in sections])
        gui.set_section_choices(sections_dict)

    # ----------------------------------------------------------------------------
    # section was selected
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_section_selected(id: int):
        # Get section id & save to the global Section variable.
        global section, course
        course: Course
        section = course.get_section_by_id(id)

        # Since we have a new section, we need to nullify the blocks.
        global gui
        gui: AssignToResourceTk
        gui.clear_blocks()

        # what blocks are available for this course/section?
        blocks = section.blocks
        blocks_dict = dict([(b.id, str(b)) for b in blocks])
        gui.set_block_choices(blocks_dict)

        # Set the default teacher for this course/section if this AssignToResource type is
        # NOT a teacher.
        global Type
        if Type == 'teacher':
            return

        teachers = section.teachers
        if len(teachers) > 0:
            global teacher
            teacher = teachers[0]
            gui.set_teacher(str(teacher))

    # ----------------------------------------------------------------------------
    # block was selected
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_block_selected(id: int):
        global block, section
        section: Section
        block = section.get_block_by_id(id)

    # ----------------------------------------------------------------------------
    # lab was selected
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_lab_selected(id: int):
        global lab
        lab: Lab = Lab.get(id)

    # ----------------------------------------------------------------------------
    # teacher was selected
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_teacher_selected(id):
        global teacher
        teacher = Teacher.get(id)

    # ----------------------------------------------------------------------------
    # add_new_section
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_add_new_section(name: str):
        #TODO: Resume from here tomorrow.
        pass
