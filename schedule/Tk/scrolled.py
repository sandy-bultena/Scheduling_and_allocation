from tkinter import *
import tkinter as tk

import sys
import traceback


def eprint(*args, **kwargs):
    print("\n", file=sys.stderr, **kwargs)
    print(*args, file=sys.stderr, **kwargs)
    print(traceback.format_stack()[0], file=sys.stderr, **kwargs)
    exit()


class Scrolled(Frame):
    """Creates a frame, creates and inserts the defined widget, and adds scrollbars

    Parameters
    ----------
    parent: Tk_container
    widget_type: str ->What widget you want to create

    Options
    -------
    scrollbars:str -> defines which scrollbars you want and where you want them: "nsew".
                      'n' is a horizontal scrollbar at the top of the widget
                      'e' is a vertical scrollbar at the right side of the widget
                      you can only have one scrollbar for horizontal and one for vertical

    all other options will be passed to the widget when it is created

    Notes
    -----
    The created object will be a frame, so you can pack or grid it as desired
    To access the scrolled widget, use 'self.widget' property

    Properties
    ----------
    widget -> the widget that you asked to be created
    horizontal_scrollbar -> the horizontal scrollbar that was created
    vertical_scrollbar -> the vertical scrollbar that was created

    Examples
    --------

    Example:
        from tkinter import *
        from scrolled import Scrolled

        mw = Tk()
        scrolled_listbox = Scrolled(mw, 'Listbox', scrollbars=E, bg='pink')
        scrolled_listbox.pack(fill=BOTH, side=TOP, expand=1)
        scrolled_listbox.vertical_scrollbar.configure(width=30)

        for i in range(20):
            scrolled_listbox.widget.insert("end", f"entry {i=}")

        mw.mainloop()

    Example
        from tkinter import *
        from scrolled import Scrolled

        mw = Tk()
        scrolled_frame = Scrolled(mw, 'Frame', scrollbars=E)
        scrolled_frame.pack(fill=BOTH, side=TOP, expand=1)

        for i in range(10):
            Button(scrolled_frame.widget,text=f"Button {i}").pack(ipady=10)

        mw.mainloop()
    """

    @property
    def widget(self):
        return self._widget

    @property
    def horizontal_scrollbar(self):
        return self._hsb

    @property
    def vertical_scrollbar(self):
        return self._vsb

    def __init__(self, parent, widget_type, scrollbars="e", **kwargs):

        self._widget = None
        # ----------------------------------------------------------------------------------------
        # get the Tk object that needs to be created
        # ----------------------------------------------------------------------------------------
        _tk_widget_type = None
        try:
            import tkinter
            _tk_widget_type = getattr(tkinter, widget_type)
        except AttributeError as e:
            eprint(str(e))

        # ----------------------------------------------------------------------------------------
        # initialize the holding frame
        # ----------------------------------------------------------------------------------------
        tkinter.Frame.__init__(self, parent)

        # ----------------------------------------------------------------------------------------
        # bail out if user is trying to create 2 scrollbars in the same orientation
        # ----------------------------------------------------------------------------------------
        self._vsb, self._hsb = None, None

        if ('e' in scrollbars and 'w' in scrollbars) or ('n' in scrollbars and 's' in scrollbars):
            _trace = traceback.format_stack()
            eprint(f"You cannot have two horizontal or two vertical scrollbars ({scrollbars=})\n" +
                   {_trace})

        # ----------------------------------------------------------------------------------------
        # create scrollbars
        # ----------------------------------------------------------------------------------------
        if 'e' in scrollbars or 'w' in scrollbars:
            self._vsb = tk.Scrollbar(self, orient=VERTICAL)
            if 'e' in scrollbars:
                self._vsb.pack(side=RIGHT, fill=Y)
            else:
                self._vsb.pack(side=LEFT, fill=Y)

        if 'n' in scrollbars or 's' in scrollbars:
            self._hsb = tk.Scrollbar(self, orient=HORIZONTAL)
            if 'n' in scrollbars:
                self._hsb.pack(side=TOP, fill=X)
            else:
                self._hsb.pack(side=BOTTOM, fill=X)

        # ----------------------------------------------------------------------------------------
        # is the widget we want to scroll, scrollable?
        # ----------------------------------------------------------------------------------------
        try:
            _xview = getattr(_tk_widget_type, "xview")
            _yview = getattr(_tk_widget_type, "yview")

            self._widget = _tk_widget_type(self, **kwargs)
            _scrollable_object = self._widget
            _scrollable_object.pack(side=TOP, fill=BOTH, expand=1)

        except AttributeError:

            # ----------------------------------------------------------------------------------------
            # the widget is not scrollable, so we are going to put it inside a canvas object
            # which is scrollable
            # ----------------------------------------------------------------------------------------
            _canvas = Canvas(self)
            _canvas.pack(side=TOP, fill=BOTH, expand=1)

            self._widget = _tk_widget_type(_canvas, **kwargs)

            _canvas.bind('<Configure>', lambda _e: _canvas.configure(scrollregion=_canvas.bbox("all")))
            _canvas.create_window((0, 0), window=self._widget, anchor="nw")

            _scrollable_object = _canvas

        # ----------------------------------------------------------------------------------------
        # bind the scrollable object to the scrollbars
        # ----------------------------------------------------------------------------------------

        if self._vsb is not None:
            self._vsb.configure(command=_scrollable_object.yview)
            _scrollable_object.configure(yscrollcommand=self._vsb.set)

        if self._hsb is not None:
            self._hsb.configure(command=_scrollable_object.hview)
            _scrollable_object.configure(xscrollcommand=self._hsb.set)


