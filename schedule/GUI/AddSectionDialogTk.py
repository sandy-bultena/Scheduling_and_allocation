"""
Add sections dialog GUI

Inputs:
    frame
Returns: 
    An array of section names
        None if Cancelled
    An array of hours for each block
        None if Cancelled
Required Event Handlers:
    -none-
"""

from tkinter import simpledialog, Frame
from MultipleDialog import MultipleDialog
import AddBlocksDialogTk

_MAX_SECTIONS = 100
_input_frame : Frame

def new(input_frame : Frame = None) -> tuple[list[str], list[int]] | None:
    """Create a new dialog instance"""
    if not input_frame: raise ValueError("Error: Add Blocks Dialog must have a parent frame")
    global _input_frame

    _input_frame = input_frame

    db_num_blocks = simpledialog.askinteger(
        title = 'How May Sections',
        prompt = f'How Many Sections? (MAX {_MAX_SECTIONS})',
        parent = _input_frame,
        minvalue = 0,
        maxvalue = _MAX_SECTIONS
        )
       
    return _process_the_sections(db_num_blocks)

def _process_the_sections(num_sections : int | None = None) -> tuple[list[str], list[int]] | None:
    """Process the sections"""
    # returns None when db_num_blocks is 0; this seems to be the intended behaviour in Perl
    if num_sections is None: return None

    db_section_names = MultipleDialog(
        parent = _input_frame,
        title = "Name The Sections",
        prompt = 'Name The Sections (OPTIONAL)',
        num_entries = num_sections,
        label_title = "",
        validation = None,
        required = False # optional
        )
    
    # if they cancelled, return
    if not db_section_names: return None
    
    section_names = db_section_names.result

    new_blocks = AddBlocksDialogTk.new(_input_frame)

    return section_names, new_blocks

if __name__ == "__main__":
    import tkinter
    print(new(tkinter.Tk()))