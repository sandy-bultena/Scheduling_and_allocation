"""Create or assign Time Blocks to various resources."""
from GUI.AssignToResourceTk import AssignToResourceTk
from Schedule.Block import Block
from Schedule.Course import Course
from Schedule.Lab import Lab
from Schedule.Schedule import Schedule
from Schedule.ScheduleEnums import ViewType
from Schedule.Section import Section
from Schedule.Stream import Stream
from Schedule.Teacher import Teacher

# ===================================================================
# globals
# ===================================================================
global course
course: Course
global section
section: Section
global block
block: Block
global teacher
teacher: Teacher
global lab
lab: Lab
global gui
gui: AssignToResourceTk


class AssignToResource:
    """Create or assign Time Blocks to various resources.

    Called with a date/time/duration of a block, as well as a Teacher/Lab.

    Allows the user to assign this block to a Course and Section,
    or to create a new block.

    or to assign an existing block to Course and Section."""
    # =================================================================
    # Class/Global Variables
    # =================================================================
    schedule: Schedule
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
        if Type == ViewType.Lab:
            global lab
            lab = schedulable
        elif Type == ViewType.Teacher:
            global teacher
            teacher = schedulable
        elif Type == ViewType.Stream or Type is None:
            return

        # ------------------------------------
        # Create Dialog Box
        # ------------------------------------
        # ViewType is not a string, so concatenating it with a + fails.
        title = f"Assign Block to {Type}"
        block_text = f"{AssignToResource.Day_name[day]} at " \
                     f"{AssignToResource._hours_to_string(start)} for {duration} hour(s)"

        global gui
        gui = AssignToResourceTk(Type)  # TODO: Implement this class.
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

        # ------------------------------------
        # setup event handlers
        # ------------------------------------
        gui.cb_course_selected(AssignToResource._cb_course_selected)
        gui.cb_section_selected(AssignToResource._cb_section_selected)
        gui.cb_block_selected(AssignToResource._cb_block_selected)
        gui.cb_teacher_selected(AssignToResource._cb_teacher_selected)
        gui.cb_lab_selected(AssignToResource._cb_lab_selected)

        gui.cb_add_new_section(AssignToResource._cb_add_new_section)
        gui.cb_add_new_block(AssignToResource._cb_add_new_block)
        gui.cb_add_new_teacher(AssignToResource._cb_add_new_teacher)
        gui.cb_add_new_lab(AssignToResource._cb_add_new_lab)

        # ------------------------------------
        # get lists of resources
        # ------------------------------------

        # labs
        lab_names = {}
        sched = AssignToResource.schedule
        for l in sched.labs():
            lab_names[l.id] = str(l)
        gui.set_lab_choices(lab_names)

        # teachers
        teacher_names = {}
        for t in sched.teachers():
            teacher_names[t.id] = str(t)
        gui.set_teacher_choices(teacher_names)

        # courses
        course_names = {}
        for course in sched.courses():
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
                # If it is, assign all properties to the Block.
                global Day, Start, Duration, lab, teacher
                block.day = Day
                block.start = AssignToResource._hours_to_string(Start)
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
        course = Course.get(id)

        # since we have a new course, we need to nullify the sections and blocks.
        global section, block, gui
        section = None
        block = None
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
        section = course.get_section_by_id(id)

        # Since we have a new section, we need to nullify the blocks.
        global gui
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
        block = section.get_block_by_id(id)

    # ----------------------------------------------------------------------------
    # lab was selected
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_lab_selected(id: int):
        global lab
        lab = Lab.get(id)

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
        global course, gui, section
        if not course:
            return  # NOTE: This will probably fail.

        # Check to see if a section by that name exists.
        sections_arr = course.get_section_by_name(name)
        section_new: Section

        # --------------------------------------------------------------------
        # Do sections with this name already exist?
        # --------------------------------------------------------------------
        if len(sections_arr) > 0:
            answer = gui.yes_no(
                "Section already exists",
                f"{len(sections_arr)} section(s) by this name already exist!\n"
                f"Do you still want to create this new section?\n\n"
                f"The name of the section will be set to something unique."
            )

            # If not, set the section to the first instance of the section with the section name.
            if answer.lower() == 'no':
                section = sections_arr[0]
                AssignToResource._cb_section_selected(section.id)
                gui.set_section(str(section))
                return

        # --------------------------------------------------------------------
        # create new section
        # --------------------------------------------------------------------
        section = Section(number=course.get_new_number(), hours=0, name=name)
        course.add_section(section)

        # --------------------------------------------------------------------
        # add the new section to the drop-down list, and make it the
        # selected section
        # --------------------------------------------------------------------
        # add to drop-down menu choices
        sections_dict = {}
        sections_arr = course.sections()
        for i in sections_arr:
            sections_dict[i.id] = str(i)

        gui.set_section_choices(sections_dict)

        gui.set_section(str(section))
        AssignToResource._cb_section_selected(section.id)

    # ----------------------------------------------------------------------------
    # add_new_block
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_add_new_block(name: str):
        global course, section
        if not course or not section:
            return  # NOTE: Verify whether this will work, or if extra validation is needed.

        global block, Day, Start, Duration
        block = Block(Day, Start, AssignToResource._hours_to_string(Duration), number=section.get_new_number())
        section.add_block(block)
        # NOTE: In the original code, the newly-created block was added to the section first,
        # and then its day, start, and duration properties were set. We can't do it that way
        # based on how Block was coded, however.

        blocks_arr = section.blocks
        blocks_dict = {}
        for i in blocks_arr:
            blocks_dict[i.id] = i.description
        global gui
        gui.set_block_choices(blocks_dict)
        # TODO: Verify whether the called function can accept actual blocks or just strings.
        gui.set_block(block)

    # ----------------------------------------------------------------------------
    # add_new_lab
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_add_new_lab(lab_name: str, lab_number: str = None):
        if not lab_number:
            return

        # See if a lab which already has that number exists.
        lab_new = Lab.get_by_number(lab_number)  # TODO: Use ScheduleWrapper instead?

        global gui, lab

        if lab_new:
            question = gui.yes_no("Create new Lab",
                                  "Lab already exists\nI won't let you do anything, okay?")
            # Regardless of the user's answer, return. (Why bother with a yes_no, then?)
            lab = None
            return

        lab = Lab(number=lab_number, descr=lab_name)

        # Add the created Lab to this schedule.
        # NOTE: In the original Perl code, we could directly assign Labs to Schedules.
        # We can't do that anymore, so we need a workaround.
        for c in AssignToResource.schedule.courses():
            c.assign_lab(lab)

        lab_names = {}
        for l in AssignToResource.schedule.labs():
            lab_names[l.id] = str(l)
        gui.set_lab_choices(lab_names)
        gui.set_lab(str(lab))

    # ----------------------------------------------------------------------------
    # add new teacher
    # ----------------------------------------------------------------------------
    @staticmethod
    def _cb_add_new_teacher(first_name: str = "", last_name: str = ""):
        my_teach: Teacher

        # Check if a first and last name have been entered, Otherwise return.
        if not first_name or not last_name:
            return

        # See if a teacher by that name already exists.
        my_teach = Teacher.get_by_name(first_name, last_name)

        global gui, teacher

        if my_teach:
            # Return if the teacher already exists. (Again, why bother asking them if the answer
            # doesn't matter?)
            question = gui.yes_no("Create new Teacher",
                                  "Teacher already exists\nI won't let you do anything, ok?")
            teacher = None
            return

        # If no teacher by that name exists, create a new one.
        teacher = Teacher(firstname=first_name, lastname=last_name)

        teacher_names = {}
        for teach in AssignToResource.schedule.teachers():
            teacher_names[teach.id] = str(teach)

        gui.set_teacher_choices(teacher_names)
        gui.set_teacher(str(teacher))

    # ----------------------------------------------------------------------------
    # _hours_to_string: 8.5 -> 8:30
    # ----------------------------------------------------------------------------
    @staticmethod
    def _hours_to_string(time: float):
        hour_string = f"{int(time)}:"
        minutes_string = "00" if time == int(time) else "30"
        return hour_string + minutes_string

