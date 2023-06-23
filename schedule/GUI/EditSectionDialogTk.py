# COMPLETED
"""
Edit section dialog GUI

Required Inputs:
    - frame
    - course name
    - section id
    - section name

Optional Inputs:
    - block_choices
    - teacher_choices
    - teacher_assigned_choices
    - stream_choices
    - stream_assigned_choices

Returns: 
    A string indicated what action was taken

Required Event Handlers:
    - cb_add_blocks_to_section            (section_id, list of blocks hours)
    - cb_remove_block_from_section        (section_id, blocks)
    - cb_edit_block                       (section_id, blocks)
    - cb_change_section_name_by_id        (section_id, name)
    - cb_remove_section_by_id             (section_id)
    - cb_add_teacher_to_section           (section_id, teacher)
    - cb_remove_teacher_from_section      (section_id, teacher)
    - cb_add_stream_to_section            (section_id, stream)
    - cb_remove_stream_from_section       (section_id, stream)

NOTE:
    - All changes occur when appropriate buttons are clicked.
    - The section name will be updated only when the dialog is closed.
"""

import AddBlocksDialogTk
# NOTE: RELIES ON Presentation.EditSectionDialog

from tkinter import simpledialog, Frame, Misc, Button, ACTIVE, LEFT, Label, Entry, StringVar, Button, messagebox
from tkinter.ttk import Combobox

class EditSectionDialog(simpledialog.Dialog):
    DROPDOWN_WIDTH = 12
    PAD = 40
    BTN_BACK = '#abcdef'

    def __init__(self, parent : Misc | None, title : str | None, section_id : int, section_name : str, **kwargs):
        """
Creates a new section edit dialog box.
# Params:
- notebook                                 -> The notebook Tk object
- title                                  -> The dialog box header
- section_id                             -> The ID of the section
- section_name                           -> The name of the section
- kwargs
    - block_choices                      -> Default options for the blocks dropdown
    - teacher_choices                    -> Default options for the add teacher dropdown
    - teacher_assigned_choices           -> Default options for the remove teacher dropdown
    - stream_choices                     -> Default options for the add stream dropdown
    - stream_assigned_choices            -> Default options for the remove stream dropdown
    - cb_add_blocks_to_section           -> Method called when blocks are added.
        - Return: updated list of section's blocks
        - Parameters: section id, list of new blocks hours
    - cb_remove_block_from_section       -> Method called when a blocks is removed.
        - Return: updated list of section's blocks
        - Parameters: section id, blocks to be removed (Schedule.Block object)
    - cb_edit_block                      -> Method called when a blocks needs to be edited.
        - Return: updated list of section's blocks
        - Parameters: section id, blocks to be edited (Schedule.Block object)
    - cb_add_teacher_to_section          -> Method called when a teacher is assigned to all blocks
        - Return: list of all teacher_ids, updated list of section's teacher_ids
        - Parameters: section id, teacher to be added (Schedule.Teacher object)
    - cb_remove_teacher_from_section     -> Method called when a teacher is removed from the section
        - Return: list of all teacher_ids, updated list of section's teacher_ids
        - Parameters: section id, teacher to be removed (Schedule.Teacher object)
    - cb_add_stream_to_section           -> Method called when a stream is added to the section
        - Return: list of all stream_ids, updated list of section's stream_ids
        - Parameters: section id, stream to be added (Schedule.Stream object)
    - cb_remove_stream_from_section      -> Method called when a stream is removed to the section
        - Return: list of all stream_ids, updated list of section's stream_ids
        - Parameters: section id, stream to be removed (Schedule.Stream object)
    - cb_change_section_name_by_id       -> Method called if the section name is changed.
        - Parameters: section id, section name
    - cb_remove_section_by_id            -> Method called if the section is deleted.
        - Parameters: section id
        """
        self.section_id = section_id
        self.section_name = section_name
        self.changed = False

        # establish starting dropdown lists
        starting_lists = [
            'block_choices',
            'teacher_choices',
            'teacher_assigned_choices',
            'stream_choices',
            'stream_assigned_choices',
        ]
        for sl in starting_lists:
            self.__setattr__('_'+sl, kwargs.get(sl, []).copy())   # copy so modifying outside list doesn't desync

        # establish presenter functions
        default_func = lambda *a : a
        expected_func = [
            'cb_add_blocks_to_section',
            'cb_remove_block_from_section',
            'cb_edit_block',
            'cb_change_section_name_by_id',
            'cb_remove_section_by_id',
            'cb_add_teacher_to_section',
            'cb_remove_teacher_from_section',
            'cb_add_stream_to_section',
            'cb_remove_stream_from_section',
            ]
        for f in expected_func: self.__setattr__(f, kwargs.get(f, default_func))

        super().__init__(parent, title)

    def body(self, parent : Frame):

        #--------------------------------------------
        # Section Name and Hours
        #--------------------------------------------
        Label(parent, text = "Section Name", anchor = "w").grid(column = 0, row = 0, sticky = 'nsew')
        self.section_name_entry = StringVar(value = self.section_name)
        Entry(parent, textvariable = self.section_name_entry).grid(column = 1, row = 0, columnspan = 3, sticky = 'nsew')
        
        Label(parent, text = "Hours", anchor = "w").grid(column = 0, row = 1, sticky = 'nsew')
        Entry(parent, textvariable = (hours_entry := StringVar())).grid(column = 1, row = 1, sticky = 'nsew')
        Label(parent, text = 'Only used if there are no blocks').grid(column = 2, row = 1, columnspan = 2, sticky = 'nsew')
        
        Label(parent, text = '').grid(columnspan = 4, row = 2, column = 0)
        
        #--------------------------------------------
        # Blocks
        #--------------------------------------------
        self._block_option = StringVar()
        self._tk_block_dropdown = Combobox(parent, textvariable = self._block_option, width = EditSectionDialog.DROPDOWN_WIDTH)
        self._tk_block_dropdown.config(state = 'readonly')
        self.update_block_choices(self._block_choices)
        self._tk_block_dropdown.grid(column = 1, row = 2, sticky = 'nsew', ipadx = EditSectionDialog.PAD)

        Label(parent, text = 'Block: ', anchor = 'w').grid(column = 0, row = 2, sticky = 'nsew')
        Button(parent, text = 'Add Block(s)', command = self._cmd_add_blocks, bg = EditSectionDialog.BTN_BACK).grid(column = 2, row = 3, sticky = 'nsew', columnspan = 2)
        Button(parent, text = 'Remove Block', command = self._cmd_remove_block, bg = EditSectionDialog.BTN_BACK).grid(column = 3, row = 2, sticky = 'nsew')
        Button(parent, text = 'Edit Block', command = self._cmd_edit_block, bg = EditSectionDialog.BTN_BACK).grid(column = 2, row = 2, sticky = 'nsew')
        
        self._tk_block_status = Label(parent, text = "")
        self._tk_block_status.grid(column = 1, row = 3, sticky = 'nsew')

        Label(parent, text = '').grid(columnspan = 4, row = 4, column = 0)
        
        #--------------------------------------------
        # Teacher Add/Remove
        #--------------------------------------------
        self._teacher_option = StringVar()
        self._tk_teacher_dropdown = Combobox(parent, textvariable = self._teacher_option, width = EditSectionDialog.DROPDOWN_WIDTH)
        self._tk_teacher_dropdown.config(state = 'readonly')
        self._tk_teacher_dropdown.grid(column = 1, row = 5, columnspan = 2, sticky = 'nsew')

        self._teacher_assigned_option = StringVar()
        self._tk_teacher_assigned_dropdown = Combobox(parent, textvariable = self._teacher_assigned_option, width = EditSectionDialog.DROPDOWN_WIDTH)
        self._tk_teacher_assigned_dropdown.config(state = 'readonly')
        self._tk_teacher_assigned_dropdown.grid(column = 1, row = 6, columnspan = 2, sticky = 'nsew')

        self.update_teacher_choices(self._teacher_choices, self._teacher_assigned_choices)

        Button(parent, text = 'Set to all blocks', command = self._cmd_add_teacher_to_all_blocks, bg = EditSectionDialog.BTN_BACK).grid(column = 3, row = 5, sticky = 'nsew')
        Label(parent, text = 'Add Teacher: ', anchor = 'w').grid(column = 0, row = 5, sticky = 'nsew')
        Button(parent, text = 'Remove from all blocks', command = self._cmd_remove_teacher_from_all_blocks, bg = EditSectionDialog.BTN_BACK).grid(column = 3, row = 6, sticky = 'nsew')
        Label(parent, text = 'Remove Teacher: ', anchor = 'w').grid(column = 0, row = 6, sticky = 'nsew')

        self._tk_teacher_status = Label(parent, text = "")
        self._tk_teacher_status.grid(columnspan = 4, row = 7, column = 0)
        
        #--------------------------------------------
        # Stream Add/Remove
        #--------------------------------------------
        self._stream_option = StringVar()
        self._tk_stream_dropdown = Combobox(parent, textvariable = self._stream_option, width = EditSectionDialog.DROPDOWN_WIDTH)
        self._tk_stream_dropdown.config(state = 'readonly')
        self._tk_stream_dropdown.grid(column = 1, row = 8, columnspan = 2, sticky = 'nsew')

        self._stream_assigned_option = StringVar()
        self._tk_stream_assigned_dropdown = Combobox(parent, textvariable = self._stream_assigned_option, width = EditSectionDialog.DROPDOWN_WIDTH)
        self._tk_stream_assigned_dropdown.config(state = 'readonly')
        self._tk_stream_assigned_dropdown.grid(column = 1, row = 9, columnspan = 2, sticky = 'nsew')

        self.update_stream_choices(self._stream_choices, self._stream_assigned_choices)

        Button(parent, text = 'Add Stream', command = self._cmd_add_stream_to_section, bg = EditSectionDialog.BTN_BACK).grid(column = 3, row = 8, sticky = 'nsew')
        Label(parent, text = 'Add Stream: ', anchor = 'w').grid(column = 0, row = 8, sticky = 'nsew')
        Button(parent, text = 'Remove Stream', command = self._cmd_remove_stream_from_section, bg = EditSectionDialog.BTN_BACK).grid(column = 3, row = 9, sticky = 'nsew')
        Label(parent, text = 'Remove Stream: ', anchor = 'w').grid(column = 0, row = 9, sticky = 'nsew')
        
        self._tk_stream_status = Label(parent, text = '')
        self._tk_stream_status.grid(columnspan = 4, column = 0, row = 10, sticky = 'n')

        col, row = parent.grid_size()
        for i in range(col): parent.grid_columnconfigure(i, weight = 1)
        parent.grid_rowconfigure(row - 1, weight = 1)

        return self._tk_block_dropdown

    def _cmd_add_blocks(self):
        block_hours = AddBlocksDialogTk.new(self)
        if block_hours:
            self.update_block_choices(self.cb_add_blocks_to_section(self.section_id, block_hours))
            self._tk_block_status.configure(text = 'Block(s) Added')
            self.bell()
        else:
            self._tk_block_status.configure(text = '')
        
        self._tk_block_status.update()

    def _cmd_remove_block(self):
        if not self._block_option.get(): return

        block = self._block_choices[self._tk_block_dropdown.current()]
        self.update_block_choices(self.cb_remove_block_from_section(self.section_id, block))
        self._tk_block_status.configure(text = 'Block Removed')
        self.bell()
        self.changed = True

    def _cmd_edit_block(self):
        if not self._block_option.get(): return

        block = self._block_choices[self._tk_block_dropdown.current()]
        self.update_block_choices(self.cb_edit_block(self.section_id, block))

    def _cmd_add_teacher_to_all_blocks(self):
        if not self._teacher_option.get(): return
        teacher = self._teacher_choices[self._tk_teacher_dropdown.current()]
        self.update_teacher_choices(*self.cb_add_teacher_to_section(self.section_id, teacher))

        self._teacher_option.set('')
        self._tk_teacher_status.configure(text = 'Teacher Added')
        self.bell()
        self._tk_teacher_status.update()
        self.changed = True

    def _cmd_remove_teacher_from_all_blocks(self):
        if not self._teacher_assigned_option.get(): return
        teacher = self._teacher_choices[self._tk_teacher_assigned_dropdown.current()]
        self.update_teacher_choices(*self.cb_remove_teacher_from_section(self.section_id, teacher))

        self._teacher_assigned_option.set('')
        self._tk_teacher_status.configure(text = 'Teacher Removed')
        self.bell()
        self._tk_teacher_status.update()
        self.changed = True

    def _cmd_add_stream_to_section(self):
        if not self._stream_option.get(): return
        stream = self._stream_choices[self._tk_stream_dropdown.current()]
        self.update_stream_choices(*self.cb_add_stream_to_section(self.section_id, stream))

        self._stream_option.set('')
        self._tk_stream_status.configure(text = 'Stream Added')
        self.bell()
        self._tk_stream_status.update()
        self.changed = True

    def _cmd_remove_stream_from_section(self):
        if not self._stream_assigned_option.get(): return
        stream = self._stream_choices[self._tk_stream_assigned_dropdown.current()]
        self.update_stream_choices(*self.cb_remove_stream_from_section(self.section_id, stream))

        self._stream_assigned_option.set('')
        self._tk_stream_status.configure(text = 'Stream Removed')
        self.bell()
        self._tk_stream_status.update()
        self.changed = True

    def buttonbox(self):
        # https://github.com/python/cpython/blob/3.11/Lib/tkinter/simpledialog.py#L165

        box = Frame(self)

        Button(box, text="Close", width=10, command=self.close, default=ACTIVE, bg = EditSectionDialog.BTN_BACK).pack(side=LEFT, padx=5, pady=5)
        Button(box, text="Delete", width=10, command=self.delete, bg = EditSectionDialog.BTN_BACK).pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.close)   # close
        self.bind("<Escape>", self.delete)  # delete

        box.pack()
    
    def delete(self, *a):
        if not messagebox.askyesno('Delete?', 'Are you sure you want to delete?', master = self): return ['break']

        self.cb_remove_section_by_id(self.section_id)
        self.result = 'Section Deleted'
        super().cancel(*a)
    
    def close(self, *a):
        if self.section_name != self.section_name_entry.get():
            self.cb_change_section_name_by_id(self.section_id, self.section_name)
        self.result = 'Section Modified' if self.changed else ''
        super().ok(*a)

    def __update_choices(self, choices : list, dropdown : str):
        """Generic dropdown choice change"""
        self.__setattr__(f'_{dropdown}_choices', list(choices).copy())
        choices = [str(i) for i in choices]
        self.__getattribute__(f'_tk_{dropdown}_dropdown')['values'] = choices
        self.__getattribute__(f'_{dropdown}_option').set_default_fonts_and_colours('')
    
    def update_block_choices(self, choices : list):
        """Update the blocks dropdown to use the provided list"""
        self.__update_choices(choices, 'blocks')
    
    def update_teacher_choices(self, choices : list, assigned_choices : list):
        """Update the teacher add and remove dropdowns to use the provided lists"""
        if choices: self.__update_choices(choices, 'teacher')
        if assigned_choices: self.__update_choices(assigned_choices, 'teacher_assigned')
    
    def update_stream_choices(self, choices : list, assigned_choices : list):
        """Update the stream add and remove dropdowns to use the provided lists"""
        if choices: self.__update_choices(choices, 'stream')
        if assigned_choices: self.__update_choices(assigned_choices, 'stream_assigned')


def new(input_frame, course_name : str, section_id : int, section_name : str, box_options : dict) -> str:
    """
    Creates a section edit dialog box with the provided options. Dialog box documentation, with detailed options info, included below:

    ----

    Creates a new section edit dialog box.
    # Params:
    - notebook                                 -> The notebook Tk object
    - title                                  -> The dialog box header
    - section_id                             -> The ID of the section
    - section_name                           -> The name of the section
    - kwargs
        - block_choices                      -> Default options for the blocks dropdown
        - teacher_choices                    -> Default options for the add teacher dropdown
        - teacher_assigned_choices           -> Default options for the remove teacher dropdown
        - stream_choices                     -> Default options for the add stream dropdown
        - stream_assigned_choices            -> Default options for the remove stream dropdown
        - cb_add_blocks_to_section           -> Method called when blocks are added.
            - Return: updated list of section's blocks
            - Parameters: section id, list of new blocks hours
        - cb_remove_block_from_section       -> Method called when a blocks is removed.
            - Return: updated list of section's blocks
            - Parameters: section id, blocks to be removed (Schedule.Block object)
        - cb_edit_block                      -> Method called when a blocks needs to be edited.
            - Return: updated list of section's blocks
            - Parameters: section id, blocks to be edited (Schedule.Block object)
        - cb_add_teacher_to_section          -> Method called when a teacher is assigned to all blocks
            - Return: list of all teacher_ids, updated list of section's teacher_ids
            - Parameters: section id, teacher to be added (Schedule.Teacher object)
        - cb_remove_teacher_from_section     -> Method called when a teacher is removed from the section
            - Return: list of all teacher_ids, updated list of section's teacher_ids
            - Parameters: section id, teacher to be removed (Schedule.Teacher object)
        - cb_add_stream_to_section           -> Method called when a stream is added to the section
            - Return: list of all stream_ids, updated list of section's stream_ids
            - Parameters: section id, stream to be added (Schedule.Stream object)
        - cb_remove_stream_from_section      -> Method called when a stream is removed to the section
            - Return: list of all stream_ids, updated list of section's stream_ids
            - Parameters: section id, stream to be removed (Schedule.Stream object)
        - cb_change_section_name_by_id       -> Method called if the section name is changed.
            - Parameters: section id, section name
        - cb_remove_section_by_id            -> Method called if the section is deleted.
            - Parameters: section id
    """
    db = EditSectionDialog(input_frame, course_name + ": Section " + section_name, section_id, section_name, **box_options)

    return db.result

if __name__ == "__main__":
    import tkinter
    blocks = ['Block 1', 'Block 2']
    teachers = ['Teacher 1', 'Teacher 2', 'Teacher 3']
    streams = ['Stream 1', 'Stream 2', 'Stream 3']

    # normally, cb_ options would have presenter logic
    # for testing purposes here, they just swap out hardcoded data
        # add_blocks            -> list of blocks should be 2 + number added
        # remove_blocks         -> list of blocks should be 1
        # edit_block            -> list of blocks should be 2
            # NOTE: The edit blocks GUI is opened by the presenter
        # add_teacher           -> list of teacher_ids should be 3, assigned teacher_ids should be 2
        # remove_teacher_by_id        -> list of teacher_ids should be 3, assigned teacher_ids should be 1 (different from starting)
        # add_stream            -> list of stream_ids should be 3, assigned stream_ids should be 2
        # remove_stream_by_id         -> list of stream_ids should be 3, assigned stream_ids should be 1 (different from starting)
    # _choices options just use hardcoded dummy strings. normally, they should be lists of objects, NOT strings
        # to start, each dropdown should contain:
            # blocks            -> 2
            # teacher_ids          -> 3
            # assigned teacher_ids -> 1
            # stream_ids           -> 3
            # assigned stream_ids  -> 1

    db_options = {
        'cb_add_blocks_to_section': lambda _, b : [*blocks, *[f'Block {i+3}' for i, _ in enumerate(b)]],
        'cb_remove_block_from_section': lambda *_: blocks[0:1],
        'cb_edit_block': lambda *_: blocks,
        'cb_add_teacher_to_section': lambda *_: (teachers, teachers[0:2]),
        'cb_remove_teacher_from_section': lambda *_: (teachers, [teachers[1]]),
        'cb_add_stream_to_section': lambda *_: (streams, streams[0:2]),
        'cb_remove_stream_from_section': lambda *_: (streams, [streams[1]]),
        'block_choices': blocks,
        'teacher_choices': teachers,
        'teacher_assigned_choices': [teachers[0]],
        'stream_choices': streams,
        'stream_assigned_choices': [streams[0]]
    }
    print(new(tkinter.Tk(), 'Course', 1, 'Section', db_options))
