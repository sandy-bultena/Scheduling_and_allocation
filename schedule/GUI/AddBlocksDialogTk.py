"""
Add blocks dialog GUI

Inputs:
    frame
Returns: 
    An array of hours for each block
        None if cancelled
Required Event Handlers:
    -none-
"""

from tkinter import simpledialog, Frame, Label, Entry, StringVar
import re

class HoursDialog(simpledialog.Dialog):
    def __init__(self, num_entries : int = 1, **kwargs):
        self.num_entries = num_entries
        super().__init__(**kwargs)

    def body(self, parent : Frame):
        parent.bind("<Return>", None)
        prompt = Label(parent, text = "How Many Hours Per Block?")        
        prompt.grid(columnspan = 2)

        col, row = parent.grid_size()
        for c in range(col): parent.grid_columnconfigure(c, weight = 1)
        parent.grid_rowconfigure(row - 1, weight = 1)

        self.hour_inputs : list[StringVar] = []
        first_entry : Entry = None
        for i in range(self.num_entries):
            self.hour_inputs.append(str_var := StringVar())
            (ent := Entry(
                parent,
                textvariable = str_var,
                validate = 'key',
                validatecommand = (self.register(
                    lambda n : bool(re.match(r'(\s*\d*\.?\d*\s*|)$', n))
                    ), '%P'),
                invalidcommand = _input_frame.bell()
                )).bind("<Return>", HoursDialog._focus_next)
            first_entry = ent if not first_entry else first_entry
            Label(parent, text = f"Block {i + 1}").grid(sticky = 'new', column = 0, row = i)
            ent.grid(column = 1, row = i)

        return first_entry

    def apply(self):
        results = []
        for i in self.hour_inputs:
            results.append(i.get())
        self.result = results
    
    def validate(self):
        # just check that they exist; numeric is being checked when they're set
        for i in self.hour_inputs:
            if not i.get(): return False
        return True
    
    @staticmethod
    def _focus_next(key):
        key.widget.tk_focusNext().focus()
        return ('break')

_MAX_BLOCKS = 10
_input_frame : Frame

def new(input_frame : Frame = None) -> list[int] | None:
    """Create a new dialog instance"""
    if not input_frame: raise ValueError("Error: Add Blocks Dialog must have a parent frame")
    global _input_frame

    _input_frame = input_frame

    db_num_blocks = simpledialog.askinteger(
        title = 'How May Blocks',
        prompt = f'How Many Blocks (MAX {_MAX_BLOCKS})',
        parent = _input_frame,
        minvalue = 0,
        maxvalue = _MAX_BLOCKS
        )
       
    return _process_block_hours(db_num_blocks)

def _process_block_hours(db_num_blocks : int | None = None) -> list[int] | None:
    """How many hours per block?"""
    # returns None when db_num_blocks is 0; this seems to be the intended behaviour in Perl
    if not db_num_blocks: return None

    db_block_hours = HoursDialog(db_num_blocks, title = "How Many Hours", parent = _input_frame)

    return db_block_hours.result if db_block_hours else None