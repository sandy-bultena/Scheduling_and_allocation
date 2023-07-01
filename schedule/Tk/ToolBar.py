from ..Tk import FindImages
from tkinter import Frame, PhotoImage, Button, Label
import os
from functools import partial
from ..Tk.idlelib_tooltip import Hovertip

# TODO: Standardize the method for cget/configure between TableEntry,
#       dynamic entry, and ToolBar.  (Best? is DynamicTree)

class ToolBar(Frame):
    def __init__(self, parent, hoverbg=None, buttonbg=None, **kwargs):
        super().__init__(master=parent, **kwargs)

        self.config_options = ['hoverbg', 'buttonbg']
        if hoverbg:
            self.configure(hoverbg=hoverbg)
        if buttonbg:
            self.configure(buttonbg=buttonbg)

        self.images = list()

        # some defaults
        image_dir = FindImages.get_image_dir()

        self.defaults = {
            'image': os.path.join(image_dir, 'default.gif')
        }

        # buttons
        self.buttons: dict[str, Button] = {}

    def configure(self, **kwargs):
        # https://stackoverflow.com/a/70568930
        # workaround to tkinter seemingly not having ConfigSpecs
        for key in self.config_options:
            if key in kwargs:
                setattr(self, key, kwargs.pop(key))
        if kwargs:
            super().configure(**kwargs)

    def config(self, **kwargs):
        self.configure(**kwargs)

    def cget(self, key):
        return getattr(self, key, None) if key in self.config_options \
            else super().cget(key)

    def add(self, **details):
        """Adds a button

        ---
        Parameters:
            - name     : str
            - image    : str (Path)
            - command  : method
            - hint     : str
            - shortcut : str
            - disabled : bool
        """

        btn_height = 20
        btn_width = 20

        # define inputs and defaults
        image_file = details.get('image', '')
        if not os.path.exists(image_file) or not os.path.isfile(image_file):
            image_file = self.defaults['image']

        name = details.get('name', os.path.basename(image_file))
        callback: callable = details.get('command', lambda *_, **__: None)
        hint = details.get('hint', '')
        shortcut_key = details.get('shortcut', [])
        disabled = details.get('disabled', False)
        bg = self.cget('buttonbg') if self.cget('buttonbg') else self.cget('bg')
        hbg = self.cget('hoverbg') if self.cget('hoverbg') else self.cget('bg')

        # define top level for this frame
        mw = self.master.winfo_toplevel()

        # define image
        image = PhotoImage(file=image_file)

        # if the image is larger than the button, roughly scale it down, so it's not auto-cropped
        # NOTE: have to save the image in object instance so that the ref does not get removed
        if btn_width < image.width() or btn_height < image.height():
            image = image.subsample(round(image.width() / btn_width),
                                              round(image.height() / btn_height))
        self.images.append(image)

        # add button
        b = Button(
            master=self,
            text=name,
            image=image,
            relief='flat',
            bg=bg,
            activebackground=bg,
            borderwidth=1,
            highlightbackground=bg,
            highlightcolor=bg,
            width=20,
            height=20
        )
        b.pack(side='left')
        self.buttons[name] = b

        # weird behaviour, using 'command=' doesn't work, but this does
        b.bind('<Button-1>', callback)

        # add the tooltip
        if hint:
            Hovertip(b, hint, 1000)

        # make the button slightly raised when mouse hovers
        # pass image to stop it from being destroyed when this method ends
        b.bind('<Enter>', partial(button_enter, b, hbg, mw, image), True)
        b.bind('<Leave>', partial(button_leave, b, bg, mw, image), True)

        # add the bindings for keypresses
        if shortcut_key:
            for sk in shortcut_key:
                mw.bind(f"<{sk}>", partial(lambda *_: b.invoke(), b))

        # disable the button?
        if disabled:
            b.configure(state='disabled')

    def bar(self):
        """Add a divider on the _toolbar"""
        Label(self, text='', bg=self.cget('bg'), relief='raised', borderwidth=1) \
            .pack(side='left', padx=3)

    def enable(self, button):
        """Enable a button"""
        self._state(1, button)

    def disable(self, button):
        """Disable a button"""
        self._state(0, button)

    def _state(self, action, name):
        if name in self.buttons and isinstance(self.buttons[name], Button):
            self.buttons[name].configure(state='normal' if action else 'disabled')


def button_enter(b: Button, hbg, mw, *_):
    b.configure(relief='raised', width=25, height=25)
    b.configure(activebackground="#000000")
    mw.update()


def button_leave(b: Button, bg, mw, *_):
    b.configure(relief='flat', width=20, height=20)
    b.configure(activebackground=bg)
    mw.update()
