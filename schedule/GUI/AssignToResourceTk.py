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
import tkinter.messagebox
from tkinter import *
from tkinter import messagebox

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
        self._frame = None
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
    def draw(self, frame, title: str, block_text: str):
        """Create and display the dialog box.

        Parameters:
            frame: A gui object that can support calls to create dialog boxes.
            title: The title of the dialog box.
            block_text: The description of the block that is the default block to assign."""
        # -----------------------------------------------
        # create dialog box
        # -----------------------------------------------
        # NOTE: tkinter doesn't have a direct analog to Perl/Tk's DialogBox. Must get creative.
        db = messagebox.askokcancel(title="Assign Block")
        self._frame = db
        global OKAY
        OKAY = db
        # TODO: FIGURE THE ABOVE STUFF OUT.
        # -----------------------------------------------
        # description of selected block
        # -----------------------------------------------
        self._new_block(block_text)

        # -----------------------------------------------
        # create labels
        # -----------------------------------------------
        self._create_main_labels(title)

        # -----------------------------------------------
        # course / section / block widgets
        # -----------------------------------------------
        self._setup_course_widgets()
        self._setup_section_widgets()
        self._setup_block_widgets()
        self._setup_teacher_widgets()
        self._setup_lab_widgets()

        # -----------------------------------------------
        # layout
        # -----------------------------------------------
        self._layout()

    def clear_sections_and_blocks(self):
        """Reset the choices for sections and blocks to empty lists, etc."""
        pass
