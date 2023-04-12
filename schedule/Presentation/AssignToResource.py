"""Create or assign Time Blocks to various resources."""
from ..GUI.AssignToResourceTk import AssignToResourceTk
from ..Schedule.Block import Block
from ..Schedule.Lab import Lab
from ..Schedule.Schedule import Schedule
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
            _open_dialog()

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
        gui.cb_course_selected(_cb_course_selected)
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
                global Day, Start, Duration, Lab, Teacher
                block.day = Day
                block.start = _hours_to_string(Start)
                block.duration = Duration
                if Lab:
                    block.assign_lab(Lab)
                if Teacher:
                    block.assign_teacher(Teacher)
                return True
        return False

