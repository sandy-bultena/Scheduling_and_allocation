# COMPLETED
"""
Add blocks dialog GUI_Pages

Inputs:
    frame
Returns: 
    An array of hours for each blocks
        None if cancelled
Required Event Handlers:
    -none-
"""

from tkinter import simpledialog, Frame
from MultipleDialog import MultipleDialog
import re

_MAX_BLOCKS = 10
_input_frame : Frame

def new(input_frame : Frame = None) -> list[int] | None:
    """Create a new dialog instance"""
    if not input_frame: raise ValueError("Error: Add Blocks Dialog must have a notebook frame")
    global _input_frame

    _input_frame = input_frame

    db_num_blocks = simpledialog.askinteger(
        title = 'How May Blocks',
        prompt = f'How Many Blocks? (MAX {_MAX_BLOCKS})',
        parent = _input_frame,
        minvalue = 0,
        maxvalue = _MAX_BLOCKS
        )
       
    return _process_block_hours(db_num_blocks)

def _process_block_hours(db_num_blocks : int | None = None) -> list[int] | None:
    """How many hours per blocks?"""
    # returns None when db_num_blocks is 0; this seems to be the intended behaviour in Perl
    if not db_num_blocks: return None

    db_block_hours = MultipleDialog(
        parent = _input_frame,
        title = "How Many Hours",
        prompt = 'How Many Hours Per Block?',
        num_entries = db_num_blocks,
        label_title = "Block {0}",
        validation = lambda n: bool(re.match(r'(\s*\d*\.?\d*\s*|)$', n))
        )
    
    # if cancelled, return
    if not db_block_hours or not db_block_hours.result: return None
    
    results = db_block_hours.result
    for i, c in enumerate(results):
        results[i] = int(c)

    return results

if __name__ == "__main__":
    import tkinter
    print(new(tkinter.Tk()))
