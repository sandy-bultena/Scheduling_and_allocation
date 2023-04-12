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
import tkinter.ttk
from functools import partial
from tkinter import *
from tkinter import messagebox
from Pmw.Pmw_2_1_1.lib.PmwComboBoxDialog import ComboBoxDialog
from Pmw.Pmw_2_1_1.lib.PmwDialog import Dialog

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
        self._frame: Dialog
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
        db_2 = Dialog(frame,
                      title="Assign Block",
                      buttons=["Ok", "Cancel"])
        self._frame = db_2
        global OKAY
        OKAY = db_2.component("Ok")
        OKAY.configure(state=DISABLED)
        OKAY.configure(width=10)
        cancel = db_2.component("Cancel")
        cancel.configure(width=10)
        # TODO: FIGURE THE ABOVE STUFF OUT. NOTE: This may or may not work.
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
        self._tb_section = ""
        sections = {}
        self.list_sections = sections
        self.set_section_choices()
        self._tk_section_new_btn_configure(state=DISABLED)

        self.clear_blocks()
        global OKAY
        OKAY.configure(state='disabled')

        # Updating the dropdown with the new options.
        self._tk_section_jbe.configure(choices=self.list_sections)
        self._tk_block_jbe.configure(choices=self.list_sections)

    def clear_blocks(self):
        """Reset the choices for blocks to empty lists, etc."""
        self._tb_block = ""
        blocks = {}
        self.list_blocks = blocks
        self.set_block_choices()
        self._tk_block_new_btn.configure(state=DISABLED)

        global OKAY
        OKAY.configure(state='disabled')

    def enable_new_section_button(self):
        self._tk_section_new_btn.configure(state=NORMAL)

    def enable_new_block_button(self):
        self._tk_block_new_btn.configure(state=NORMAL)

    def set_teacher(self, teacher_name: str):
        self._tb_teacher(teacher_name)
        self._new_teacher_lname = ""
        self._new_teacher_fname = ""

    def set_section(self, section_name):
        self._tb_section(section_name)
        self._new_section = ""

    def set_block(self, block_name):
        self._tb_block(block_name)
        self._new_block = ""
        global OKAY
        OKAY.configure(state=NORMAL)

    def set_lab(self, lab_name):
        self._tb_lab(lab_name)
        self._new_lab_name = ""
        self._new_lab_number = ""

    def set_lab_choices(self, labs: dict[int, str]):
        self.list_labs.update(labs)
        self._tk_lab_jbe.configure(choices=self.list_labs)

    def set_teacher_choices(self, teachers: dict[int, str]):
        self.list_teachers.update(teachers)
        self._tk_teacher_jbe.configure(choices=self.list_teachers)

    def set_course_choices(self, courses: dict[int, str]):
        self.list_courses.update(courses)
        self._tk_course_jbe.configure(choices=self.list_courses)
        global OKAY
        OKAY.configure(state=DISABLED)

    def set_section_choices(self, sections):
        self.list_sections.update(sections)
        self._tk_section_jbe.configure(choices=self.list_sections)
        self.enable_new_section_button()
        global OKAY
        OKAY.configure(state=DISABLED)

    def set_block_choices(self, blocks):
        self.list_blocks.update(blocks)
        self._tk_block_jbe.configure(choices=self.list_blocks)
        self.enable_new_block_button()
        global OKAY
        OKAY.configure(state=DISABLED)

    def show(self):
        return self._frame.show()

    def yes_no(self, title, question):
        """Displays a yes/no dialog.

        Parameters:
            title: Title of the dialog box.
            question: Question asked by the dialog box."""
        db = Dialog(self._frame,
                    title=title,
                    buttons=["Yes", "No"])
        Label(db, text=question).pack()
        return db.show() or ""

    # ============================================================================
    # course
    # ============================================================================
    def _setup_course_widgets(self):
        db = self._frame

        # self._tk_course_jbe(
        #     # Pmw equivalent of JBrowseEntry seems to be this, at least at first glance.
        #     ComboBoxDialog(db,
        #              )
        # )
        def browse_cmd(self):
            id = _get_id(self.list_courses, self._tb_course)
            self.cb_course_selected(id)  # TODO: Figure out if this partial works.

        # Pmw equivalent of JBrowseEntry seems to be this, at least at first glance.
        self._tk_course_jbe = ComboBoxDialog(db,
                                             scrolledlist_items=self._tb_course_ptr,
                                             selectioncommand=partial(
                                                 browse_cmd, self))

        course_drop_entry = self._tk_course_jbe.component("entry")
        course_drop_entry.configure(disabledbackground="white")
        course_drop_entry.configure(disabledforeground="black")

    # ============================================================================
    # section
    # ============================================================================
    def _setup_section_widgets(self):
        db = self._frame

        def browse_cmd(self):
            id = _get_id(self.list_sections, self._tb_section)
            self.cb_section_selected(id)

        self._tk_section_jbe = ComboBoxDialog(db,
                                              scrolledlist_items=self._tb_section_ptr,
                                              selectioncommand=partial(
                                                  browse_cmd, self
                                              ))

        sec_drop_entry: Entry = self._tk_section_jbe.component("entry")
        sec_drop_entry.configure(disabledbackground="white")
        sec_drop_entry.configure(disabledforeground="black")

        self._tk_section_entry = Entry(db,
                                       textvariable=self._new_section_ptr)

        def add_new_section(self):
            self.cb_add_new_section(self._new_section)

        self._tk_section_new_btn = Button(db,
                                          text="Create",
                                          state=DISABLED,
                                          width=20,
                                          command=partial(
                                              add_new_section, self
                                          ))

    # ============================================================================
    # block
    # ============================================================================
    def _setup_block_widgets(self):
        db = self._frame

        def browse_cmd(self):
            id = _get_id(self.list_blocks, self._tb_block)
            self.cb_block_selected(id)

        self._tk_block_jbe = ComboBoxDialog(db,
                                            scrolledlist_items=self._tb_block_ptr,
                                            width=20,
                                            selectioncommand=partial(
                                                browse_cmd, self
                                            ))

        block_drop_entry: Entry = self._tk_block_jbe.component("entry")
        block_drop_entry.configure(disabledbackground="white")
        block_drop_entry.configure(disabledforeground="black")

        self._tk_block_entry = Entry(db,
                                     textvariable=self._new_block_ptr,
                                     state=DISABLED,
                                     disabledbackground='white')

        def new_block_clicked(self):
            self.cb_add_new_block(self._new_block)
            self._tk_block_new_btn.configure(state=DISABLED)
            self._tk_block_entry.configure(state=DISABLED)

        self._tk_block_new_btn = Button(db,
                                        text="Create",
                                        state=DISABLED,
                                        command=partial(
                                            new_block_clicked, self
                                        ))

    # ============================================================================
    # teachers
    # ============================================================================
    def _setup_teacher_widgets(self):
        db = self._frame

        def browse_cmd(self):
            id = _get_id(self.list_teachers, self._tb_teacher)
            self.cb_teacher_selected(id)

        self._tk_teacher_jbe = ComboBoxDialog(
            db,
            scrolledlist_items=self._tb_teacher_ptr,
            width=20,
            selectioncommand=partial(
                browse_cmd, self
            )
        )

        teacher_drop_entry: Entry = self._tk_teacher_jbe.component("entry")
        teacher_drop_entry.configure(disabledbackground="white")
        teacher_drop_entry.configure(disabledforeground="black")

        self._tk_fname_entry = Entry(db, textvariable=self._new_teacher_fname_ptr)
        self._tk_lname_entry = Entry(db, textvariable=self._new_teacher_lname_ptr)

        def new_teacher_clicked(self):
            self.cb_add_new_teacher(self._new_teacher_fname, self._new_teacher_lname)

        self._tk_teacher_new_btn = Button(
            db,
            text="Create",
            command=partial(
                new_teacher_clicked, self
            )
        )

    # ======================================================
    # Lab
    # ======================================================
    def _setup_lab_widgets(self):
        db = self._frame

        def browse_cmd(self):
            id = _get_id(self.list_labs, self._tb_lab)
            self.cb_lab_selected(id)

        self._tk_lab_jbe = ComboBoxDialog(
            db,
            scrolledlist_items=self._tb_lab_ptr,
            state='readonly',
            width=20,
            selectioncommand=partial(
                browse_cmd, self
            )
        )

        lab_drop_entry: Entry = self._tk_lab_jbe.component("entry")
        lab_drop_entry.configure(disabledbackground="white")
        lab_drop_entry.configure(disabledforeground="black")

        self._tk_lab_num_entry = Entry(db, textvariable=self._new_lab_number_ptr)
        self._tk_lab_descr_entry = Entry(db, textvariable=self._new_lab_name_ptr)

        def new_lab_clicked(self):
            self.cb_add_new_lab(self._new_lab_name, self._new_lab_number)

        self._tk_lab_new_btn = Button(
            db,
            text="Create",
            command=partial(
                new_lab_clicked, self
            )
        )

    # ----------------------------------------------------------------------------
    # Create Main Labels
    # ----------------------------------------------------------------------------
    @staticmethod
    def _label(db, text: str, options: dict):
        return Label(db, options, text=text)

    def _create_main_labels(self, main_title):
        # Dictionary of options to pass to _label.
        opts = {}

        db = self._frame

        global big_font
        self._lbl_title = AssignToResourceTk._label(db, main_title, {'font': big_font})
        # Most subsequent calls will be anchored to the west side of the screen.
        opts = {'anchor': 'w'}
        self._lbl_course = AssignToResourceTk._label(db, "Choose Course", opts)
        self._lbl_lab = AssignToResourceTk._label(db, "Choose Lab", opts)
        self._lbl_teacher = AssignToResourceTk._label(db, "Choose Teacher", opts)
        self._lbl_section = AssignToResourceTk._label(db, "Choose Section", opts)
        self._lbl_block = AssignToResourceTk._label(db, "Choose Block to Modify", opts)

        self._lbl_create_section = AssignToResourceTk._label(db, "Create new from Section Name",
                                                             opts)
        self._lbl_create_teacher = AssignToResourceTk._label(db, "Create new Firstname / Lastname",
                                                             opts)
        self._lbl_create_lab = AssignToResourceTk._label(db, "Create new from Lab number and name",
                                                         opts)
        self._lbl_create_block = AssignToResourceTk \
            ._label(db, "Create block from selected date/time", opts)

        # Remaining labels will be bolded and anchored to the west.
        opts = {'font': bold_font, 'anchor': 'w'}
        self._lbl_course_info = AssignToResourceTk._label(db, "Course Info (required)", opts)
        self._lbl_teacher_info = AssignToResourceTk._label(db, "Teacher (optional)", opts)
        self._lbl_lab_info = AssignToResourceTk._label(db, "Lab (optional)", opts)

    def _layout(self):
        db = self._frame

        # -------------------------------------------------------
        # title
        # -------------------------------------------------------
        # NOTE: the "-", "-", "-" in the Perl code indicates relative placement: each "-" increases
        # the columnspan to the left. Tkinter has no equivalent to this.
        self._lbl_title.grid(padx=2, sticky='nsew')

        # -------------------------------------------------------
        # course
        # -------------------------------------------------------
        Label(db, text='').grid(sticky='nsew')
        self._lbl_course_info.grid(padx=2, sticky='nsew')
        self._lbl_course.grid(padx=2, sticky='nsew')
        self._tk_course_jbe.grid(padx=2, sticky='nsew')

        # -------------------------------------------------------
        # section
        # -------------------------------------------------------
        self._lbl_section.grid(self._lbl_create_section, padx=2, sticky='nsew')
        self._tk_section_jbe.grid(self._tk_section_entry, "-", self._tk_section_new_btn,
                                  padx=2,
                                  sticky='nsew')

        # -------------------------------------------------------
        # block
        # -------------------------------------------------------
        self._lbl_block.grid(self._lbl_create_block,
                             "-", "-",
                             padx=2,
                             sticky='nsew')
        self._tk_block_jbe.grid(self._tk_block_entry, "-", self._tk_block_new_btn,
                                padx=2,
                                sticky='nsew')

        # -------------------------------------------------------
        # teacher
        # -------------------------------------------------------
        global Type
        if Type != "teacher":
            Label(db, text='').grid("-", padx=2, sticky='nsew')
            self._lbl_teacher_info.grid(
                "-", "-", "-", padx=2, sticky='nsew'
            )
            self._lbl_teacher.grid(
                self._lbl_create_teacher,
                "-", "-",
                padx=2,
                sticky='nsew'
            )
            self._tk_teacher_jbe.grid(
                self._tk_fname_entry, self._tk_lname_entry,
                self._tk_teacher_new_btn,
                sticky='nsew',
                padx=2
            )
            Label(db, text='').grid("-", "-", "-", padx=2, sticky='nsew')

        # -------------------------------------------------------
        # lab
        # -------------------------------------------------------
        if Type != 'lab':
            Label(db, text='').grid("-", "-", "-", padx=2, sticky='nsew')
            self._lbl_lab_info.grid(
                "-", "-", "-",
                padx=2,
                sticky='nsew'
            )
            self._lbl_lab.grid(
                self._lbl_create_lab,
                "-", "-",
                padx=2,
                sticky='nsew'
            )
            self._tk_lab_jbe.grid(
                self._tk_lab_num_entry, self._tk_lab_descr_entry,
                self._tk_lab_new_btn,
                sticky='nsew',
                padx=2
            )
            Label(db, text='').grid("-", "-", "-", padx=2, sticky='nsew')

    # ============================================================================
    # setup getters and setters
    # ============================================================================
    def __setup(self):
        # ------------------------------------------------------------------------
        # Entry or Text Box variable bindings
        # ------------------------------------------------------------------------
        AssignToResourceTk._create_setters_and_getters(
            category='list',
            properties=["courses", "sections", "blocks", "teachers", "labs"],
            default={}
        )

        AssignToResourceTk._create_setters_and_getters(
            category="_tb",
            properties=["course", "section", "block", "teacher", "lab"],
            default=""
        )

        AssignToResourceTk._create_setters_and_getters(
            category="_new",
            properties=["section, teacher_fname", "teacher_lname", "lab_number", "lab_name", "block"],
            default=""
        )

        # ------------------------------------------------------------------------
        # getters and setters for callback routines
        # ------------------------------------------------------------------------
        callbacks = [
            "add_new_section",
            "section_selected",
            "course_selected",
            "block_selected",
            "teacher_selected",
            "lab_selected",
            "add_new_block",
            "add_new_teacher",
            "add_new_lab"
        ]
        def default_cb():
            return

        AssignToResourceTk._create_setters_and_getters(
            category="cb",
            properties=callbacks,
            default=default_cb
        )

        # ------------------------------------------------------------------------
        # Tk Labels
        # ------------------------------------------------------------------------
        labels = ["title", "selected_block", "course_info", "teacher_info", "lab_info",
                  "course", "teacher", "lab", "section", "block", "create_section",
                  "create_teacher", "create_lab", "create_block"
                  ]

        AssignToResourceTk._create_setters_and_getters(
            category="_lbl",
            properties=labels,
            default=None
        )

        # ------------------------------------------------------------------------
        # Defining widget getters and setters
        # ------------------------------------------------------------------------
        widgets = [
            "course_jbe", "section_jbe", "teacher+jbe", "lab_jbe", "block_jbe",
            "section_entry", "fname_entry", "lname_entry", "block_entry", "lab_descr_entry", "lab_num_entry",
            "section_new_btn", "teacher_new_btn", "block_new_btn", "lab_new_btn"
        ]
        AssignToResourceTk._create_setters_and_getters(
            category="_tk",
            properties=widgets,
            default=None
        )

    # ============================================================================
    # getters and setters
    # - creates two subs for each property
    # 1) cat_property
    # 2) cat_property_ptr
    # ============================================================================
    @staticmethod
    def _create_setters_and_getters(*, category, properties: list, default):
        cat = category
        props = properties

        def make_prop(name: str, default):
            def name(self):
                return eval(f"{self}.{name}") or default

        for prop in props:
            #  Create a simple getter and setter.
            name = f"{cat}_{prop}"
        # TODO: Finish this method, or find an alternative.
        pass

    @staticmethod
    def _get_id(hash_ptr: dict, name):
        # my_ref = reversed(hash_ptr)
        # return my_ref[name]
        # More Pythonic way of doing this, taken from here.
        # https://stackoverflow.com/questions/483666/reverse-invert-a-dictionary-mapping
        inverted_hash = {v: k for k, v in hash_ptr}
        return inverted_hash[name]



