import sys
from os import path
sys.path.append(path.dirname(path.dirname(__file__)))

from tkinter import simpledialog, Frame, Label, Entry, StringVar
from typing import Callable
from Tk.scrolled import Scrolled

class MultipleDialog(simpledialog.Dialog):
    SCROLL_AMOUNT = 15

    def __init__(self,
                 parent, title : str, prompt : str = "", num_entries : int = 1,
                 label_title : str = "{0}", validation : Callable[[str], bool] = None,
                 required : bool = True):
        """
        - parent      -> Parent frame
        - title       -> Title of dialog window
        - prompt      -> Prompt shown under header
        - num_entries -> Number of inputs to take from the user
        - label_title -> Display text for the input prompts. "{0}" will be replaced by the input number
        - validation  -> Method called to validate input. "None" for no validation. Must take 1 input parameter
        - required    -> Whether every input must be filled. Defaults to True
        """
        self.num_entries = num_entries
        self.label_title = label_title
        self.prompt = prompt
        self.validation = validation
        self.required = required
        super().__init__(parent, title)

    def body(self, parent : Frame):
        parent.bind("<Return>", None)

        self.hour_inputs : list[StringVar] = []
        first_entry : Entry = None
        
        if self.num_entries >= MultipleDialog.SCROLL_AMOUNT:
            (scroll := Scrolled(
                parent = parent,
                widget_type = "Frame",
                scrollbars = 'oe',
                width = 300,
                height = 300)).pack(expand = True, fill = 'both')
            scroll_f : Frame = scroll.widget
            scroll_f.master.config()
            Label(scroll_f, text = self.prompt).pack(side = 'top')

            # scroll frame refuses to fill 300x300            
            #scroll_f.master.master.master.master.configure(background = 'purple')  # dialog window
            #scroll_f.master.master.master.configure(background = 'black')          # dialog frame (shouldn't be seen)
            #scroll_f.master.master.configure(background = 'blue')                  # scroll
            #scroll_f.master.configure(background = 'red')                          # scroll canvas (shouldn't be seen?)
            #scroll_f.configure(background = 'pink')                                # scroll frame
        else:
            Label(parent, text = self.prompt).grid(columnspan = 2, row = 0)
            col, row = parent.grid_size()
            for c in range(col): parent.grid_columnconfigure(c, weight = 1)
            parent.grid_rowconfigure(row - 1, weight = 1)
                
        for i in range(self.num_entries):
            self.hour_inputs.append(str_var := StringVar())
            ent_options = {
                'textvariable': str_var,
                'validate': 'key',
                'validatecommand': (self.register(self.validation), '%P') if self.validation else None
            }
            

            # using Scrolled, so use pack
            if self.num_entries >= MultipleDialog.SCROLL_AMOUNT:
                (x := Frame(scroll_f)).pack(fill = 'x', padx = 5, pady = 5)

                (ent := Entry(x, invalidcommand = x.bell(), **ent_options))\
                    .pack(side = 'right' if self.label_title else 'left', expand = True, fill = 'x')
                ent.bind("<FocusIn>", lambda a : scroll.see_widget(a.widget))

                if self.label_title:
                    Label(x, text = self.label_title.format(str(i + 1).zfill(
                        len(str(self.num_entries))
                    ))).pack(side = 'left', expand = True, fill = 'x')
            
            # not using Scrolled, so use grid
            else:
                (ent := Entry(parent, invalidcommand = parent.bell(), **ent_options))\
                    .grid(column = 1, row = i + 1)
                Label(parent, text = self.label_title.format(str(i + 1).zfill(
                    len(str(self.num_entries))
                ))).grid(sticky = 'new', column = 0, row = i + 1)
            
            ent.bind("<Return>", MultipleDialog._focus_next)
            first_entry = ent if not first_entry else first_entry
        
        return first_entry

    def apply(self):
        results = []
        for i in self.hour_inputs:
            results.append(i.get())
        self.result = results
    
    def validate(self):
        # just check that they exist; validation is being checked when they're set
        if self.required:
            for i in self.hour_inputs:
                if not i.get(): return False
        
        return True
    
    @staticmethod
    def _focus_next(key):
        key.widget.tk_focusNext().focus()
        return ('break')