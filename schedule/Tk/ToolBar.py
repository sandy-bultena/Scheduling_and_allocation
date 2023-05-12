from ..Tk import FindImages
from tkinter import Frame, PhotoImage, Button, Label
import os
from functools import partial
from idlelib.tooltip import Hovertip

# TODO: hoverbg doesn't work tkinter... need to explicitly tie it to the <enter> and <leave> events.
#       NOTE: not a big deal
class ToolBar(Frame):
    def __init__(self, parent, hoverbg=None, buttonbg=None, **kwargs):
        super().__init__(master=parent, **kwargs)

        self.config_options = ['hoverbg', 'buttonbg']
        if hoverbg: self.configure(hoverbg=hoverbg)
        if buttonbg: self.configure(buttonbg=buttonbg)

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
            if key in kwargs: setattr(self, key, kwargs.pop(key))
        if kwargs: super().configure(**kwargs)

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
        callback = details.get('command', lambda *_, **__: {})
        hint = details.get('hint', '')
        shortcut_key = details.get('shortcut', [])
        disabled = details.get('disabled', False)
        bg = self.cget('buttonbg') if self.cget('buttonbg') else self.cget('bg')
        hbg = self.cget('hoverbg') if self.cget('hoverbg') else self.cget('bg')

        # define top level for this frame
        mw = self.master.winfo_toplevel()

        # define image
        image = PhotoImage(file=image_file)
        # if the image is larger than the button, roughly scale it down so its not auto-cropped
        if btn_width < image.width() or btn_height < image.height():
            image = image.subsample(round(image.width() / btn_width), round(image.height() / btn_height))

        # add button
        (b := Button(
            master=self,
            text=name,
            image=image,
            command=callback,
            relief='flat',
            bg=bg,
            activebackground=bg,
            borderwidth=1,
            highlightbackground=bg,
            highlightcolor=bg,
            width=20,
            height=20
        )).pack(side='left')
        self.buttons[name] = b

        # no idea why this is needed, but without it the buttons randomly don't call callback
        b.bind('<Button-1>', callback)

        # add the tooltip
        if hint: Hovertip(b, hint, 500)

        # make the button slightly raised when mouse hovers
        # pass image to stop it from being destroyed when this method ends
        b.bind('<Enter>', partial(button_enter, b, hbg, mw, image), True)
        b.bind('<Leave>', partial(button_leave, b, bg, mw, image), True)

        # add the bindings for keypresses
        if shortcut_key:
            for sk in shortcut_key: mw.bind(f"<{sk}>", partial(lambda *_: b.invoke(), b))

        # disable the button?
        if disabled: b.configure(state='disabled')

    def bar(self):
        """Add a divider on the toolbar"""
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


def button_enter(b: Button, hbg, mw, image=None, *_):
    b.configure(relief='raised')
    b.configure(activebackground=hbg)
    mw.update()

def button_leave(b: Button, bg, mw, image=None, *_):
    b.configure(relief='flat')
    b.configure(activebackground=bg)
    mw.update()
