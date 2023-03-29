# Currently not working
# NOTE: RELIES ON Presentation.EditSectionDialog

# grid seems to work different in tkinter - seemingly doesn't support .grid(widget1, widget2, "-", widget3) style setup
    # if true, this whole file needs to reworked to use explicit column/row/columnspan

from tkinter import simpledialog, Frame, Misc, Button, ACTIVE, LEFT, Label, Entry, StringVar, OptionMenu, Button, messagebox

class EditSectionDialog(simpledialog.Dialog):
    DROPDOWN_WIDTH = 12
    PAD = 40

    def __init__(self, parent : Misc | None, title : str | None, section_id : int, section_name : str):
        self.section_id = section_id
        self.old_section_name = self.section_name = section_name
        self.changed = ''
        super().__init__(parent, title)

    def body(self, parent : Frame):

        #--------------------------------------------
        # Section Name and Hours
        #--------------------------------------------
        Label(parent, text = "Section Name", anchor = "w").grid(
            Entry(textvariable = (section_name_entry := StringVar())), '-', '-', sticky = 'nsew')
        
        Label(parent, text = "Hours", anchor = "w").grid(
            Entry(textvariable = (hours_entry := StringVar())), Label(text = 'Only used if there are no blocks'), '-', sticky = 'nsew')
        
        Label(text = '').grid(columnspan = 4)
        
        #--------------------------------------------
        # Blocks
        #--------------------------------------------
        self.block_option = StringVar()
        self._tk_block_dropdown = OptionMenu(parent, self.block_option, '')
        self._tk_block_dropdown.grid(column = 1, row = 2, sticky = 'nsew', ipadx = EditSectionDialog.PAD)
        self._tk_block_dropdown.config(width = EditSectionDialog.DROPDOWN_WIDTH)
        # potentially set back/fore ground of optionmenu

        Label(parent, text = 'Block: ', anchor = 'w').grid(column = 0, row = 2, sticky = 'nsew')
        Button(parent, text = 'Add Block(s)', command = self._cmd_add_blocks).grid(column = 2, row = 3, sticky = 'nsew', columnspan = 2)
        Button(parent, text = 'Remove Block', command = self._cmd_remove_block).grid(column = 3, row = 2, sticky = 'nsew')
        Button(parent, text = 'Edit Block', command = self._cmd_edit_block).grid(column = 2, row = 2, sticky = 'nsew')
        
        self._tk_block_status = Label(parent, text = "")
        self._tk_block_status.grid(column = 1, row = 3, sticky = 'nsew')

        Label(parent, text = '').grid(columnspan = 4)
        
        #--------------------------------------------
        # Teacher Add/Remove
        #--------------------------------------------
        self.teacher_option = StringVar()
        self._tk_teacher_dropdown = OptionMenu(parent, self.teacher_option, '')
        self._tk_teacher_dropdown.config(width = EditSectionDialog.DROPDOWN_WIDTH)
        # potentially set back/fore ground of optionmenu

        self.teacher_assigned_option = StringVar()
        self._tk_teacher_assigned_dropdown = OptionMenu(parent, self.teacher_assigned_option, '')
        self._tk_teacher_assigned_dropdown.config(width = EditSectionDialog.DROPDOWN_WIDTH)
        # potentially set back/fore ground of optionmenu

        teacher_add_btn = Button(parent, text = 'Set to all blocks', command = self._cmd_add_teacher_to_all_blocks)
        Label(parent, text = 'Add Teacher: ', anchor = 'w').grid(self._tk_teacher_dropdown, '-', teacher_add_btn, sticky = 'nsew')
        teacher_remove_btn = Button(parent, text = 'Set to all blocks', command = self._cmd_remove_teacher_from_all_blocks)
        Label(parent, text = 'Remove Teacher: ', anchor = 'w').grid(self._tk_teacher_assigned_dropdown, '-', teacher_remove_btn, sticky = 'nsew')

        (_tk_teacher_status := Label(parent, text = "")).grid(columnspan = 4)
        
        #--------------------------------------------
        # Stream Add/Remove
        #--------------------------------------------
        self.stream_option = StringVar()
        self._tk_stream_dropdown = OptionMenu(parent, self.stream_option, '')
        self._tk_stream_dropdown.config(width = EditSectionDialog.DROPDOWN_WIDTH)
        # potentially set back/fore ground of optionmenu

        self.stream_assigned_option = StringVar()
        self._tk_stream_assigned_dropdown = OptionMenu(parent, self.stream_assigned_option, '')
        self._tk_stream_assigned_dropdown.config(width = EditSectionDialog.DROPDOWN_WIDTH)
        # potentially set back/fore ground of optionmenu

        stream_add_btn = Button(parent, text = 'Add Stream', command = self._cmd_add_stream_to_section)
        Label(parent, text = 'Add Stream: ', anchor = 'w').grid(self._tk_stream_dropdown, '-', stream_add_btn, sticky = 'nsew')
        stream_remove_btn = Button(parent, text = 'Remove Stream', command = self._cmd_remove_stream_from_section)
        Label(parent, text = 'Remove Stream: ', anchor = 'w').grid(self._tk_stream_assigned_dropdown, '-', stream_remove_btn, sticky = 'nsew')
        
        self._tk_stream_status = Label(parent, text = '')
        self._tk_stream_status.grid(columnspan = 4, sticky = 'n')

        col, row = parent.grid_size()
        for i in range(col): parent.grid_columnconfigure(i, weight = 1)
        parent.grid_rowconfigure(row - 1, weight = 1)

        return self._tk_block_dropdown

    def _cmd_add_blocks(self):
        pass

    def _cmd_remove_block(self):
        pass

    def _cmd_edit_block(self):
        pass

    def _cmd_add_teacher_to_all_blocks(self):
        pass

    def _cmd_remove_teacher_from_all_blocks(self):
        pass

    def _cmd_add_stream_to_section(self):
        pass

    def _cmd_remove_stream_from_section(self):
        pass

    def buttonbox(self):
        # https://github.com/python/cpython/blob/3.11/Lib/tkinter/simpledialog.py#L165

        box = Frame(self)

        Button(box, text="Close", width=10, command=self.ok, default=ACTIVE).pack(side=LEFT, padx=5, pady=5)
        Button(box, text="Delete", width=10, command=self.cancel).pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)      # close
        self.bind("<Escape>", self.cancel)  # delete

        box.pack()
    
    def cancel(self, *a):
        if messagebox.askyesno('Delete?', 'Are you sure you want to delete?'): return ['break']

        self.cb_remove_section_by_id(self.section_id)
        return 'Section Deleted'
    
    def ok(self, *a):
        if self.section_name != self.old_section_name:
            self.cb_change_section_name_by_id(self.section_id, self.section_name)
        return self.changed


_input_frame : Misc

def new(input_frame, course_name : str, section_id : int, section_name : str):
    global _input_frame
    _input_frame = input_frame

    db = EditSectionDialog(_input_frame, course_name + ": Section " + section_name, section_id, section_name)


if __name__ == "__main__":
    import tkinter
    print(new(tkinter.Tk(), 'Course', 1, 'Section'))