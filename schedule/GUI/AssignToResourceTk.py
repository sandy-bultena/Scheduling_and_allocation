"""Gui companion to AssignToResource object.

REQUIRED EVENT HANDLERS:

* cb_course_selected(course_id)
* cb_section_selected(section_id)
* cb_block_selected(block_id)
* cb_teacher_selected(teacher_id)
* cb_lab_selected(lab_id)
* cb_add_new_section(section_name)
* cb_add_new_block(block_description)
* cb_add_new_teacher(firstname, lastname)
* cb_add_new_lab(lab_name, lab_number)"""

# ============================================================================
# globals
# ============================================================================
global fonts
global big_font
global bold_font
global OKAY
global Type

global __setup


class AssignToResourceTk:
    """Gui companion to AssignToResource object.

    REQUIRED EVENT HANDLERS:

    * cb_course_selected(course_id)
    * cb_section_selected(section_id)
    * cb_block_selected(block_id)
    * cb_teacher_selected(teacher_id)
    * cb_lab_selected(lab_id)
    * cb_add_new_section(section_name)
    * cb_add_new_block(block_description)
    * cb_add_new_teacher(firstname, lastname)
    * cb_add_new_lab(lab_name, lab_number)"""
    # ============================================================================
    # constructor
    # ============================================================================
    def __init__(self, type):
        """
        Create an instance of AssignToResourceTk object, but does NOT draw the
        dialog box at this point. This allows the calling function to set up the
        callback routines first, as well as the lists for courses, etc.

        Parameters:
            type: The type of schedulable object (Teacher/Lab/Stream).

        [Don't use Stream. This GUI is not set up for it.]
        """
        global Type
        Type = type

        # set fonts TODO: Implement the FontsAndColoursTk class.
        global fonts
        fonts = FontsAndColoursTk.Fonts
        global big_font
        big_font = fonts['bigbold']
        global bold_font
        bold_font = fonts['bold']

    # ============================================================================
    # draw
    # ============================================================================
    def draw(self, frame, title, block_text):
        pass