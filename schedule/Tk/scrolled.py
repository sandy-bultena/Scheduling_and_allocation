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


    Properties
    ----------
    widget -> the widget that you asked to be created
    horizontal_scrollbar -> the horizontal scrollbar that was created
    vertical_scrollbar -> the vertical scrollbar that was created

    horizontal_scrollbar

    vertical_scrollbar

    Methods
    -------
    see_widget (self,internal_widget)
     - will adjust the scrollable region so that the internal widget within the scrollable region will
       be visible

    see(self) TODO: for text_widget or the like, see a particular line?

    Notes
    -----
    The created object will be a frame, so you can pack or grid it as desired
    To access the scrolled widget, use 'self.widget' property
    To access the scrollbars, use self.horizontal_scrollbar and self.vertical_scrollbar
     - scrollbars have been set to not take focus, if you want to change that you have to modify
       the scrollbars after the scrolled widget has been created


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

    # ==============================================================================================
    # properties
    # ==============================================================================================
    @property
    def widget(self):
        return self._widget

    @property
    def horizontal_scrollbar(self):
        return self._hsb

    @property
    def vertical_scrollbar(self):
        return self._vsb

    # ==============================================================================================
    # constructor
    # ==============================================================================================
    def __init__(self, parent, widget_type, scrollbars="e", **kwargs):
        """ constructs scrollbars, widget from widget_type, attaches them appropriately

        a frame will be created (self)
        a widget of widget type will be created inside the frame (self.widget)
        scrollbars will be created as requested (self.horizontal_scrollbar, self.vertical_scrollbar)
        """
        self._scrollable_object = None
        self._vsb = None
        self._hsb = None
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
        if ('e' in scrollbars and 'w' in scrollbars) or ('n' in scrollbars and 's' in scrollbars):
            _trace = traceback.format_stack()
            eprint(f"You cannot have two horizontal or two vertical scrollbars ({scrollbars=})\n" +
                   {_trace})

        # ----------------------------------------------------------------------------------------
        # create scrollbars
        # ----------------------------------------------------------------------------------------
        if 'e' in scrollbars or 'w' in scrollbars:
            self._vsb = tk.Scrollbar(self, orient=VERTICAL, takefocus=0)
            if 'e' in scrollbars:
                self._vsb.pack(side=RIGHT, fill=Y)
            else:
                self._vsb.pack(side=LEFT, fill=Y)

        if 'n' in scrollbars or 's' in scrollbars:
            self._hsb = tk.Scrollbar(self, orient=HORIZONTAL, takefocus=0)
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
            self._scrollable_object = self._widget
            self._scrollable_object.pack(side=TOP, fill=BOTH, expand=1)

        except AttributeError:

            # ----------------------------------------------------------------------------------------
            # the widget is not scrollable, so we are going to put it inside a canvas object
            # which is scrollable
            # ----------------------------------------------------------------------------------------
            canvas_args = {}
            if 'width' in kwargs: canvas_args['width'] = kwargs['width']
            if 'height' in kwargs: canvas_args['height'] = kwargs['height']
            _canvas = Canvas(self, **canvas_args)
            _canvas.pack(side=TOP, fill=BOTH, expand=1)

            self._widget = _tk_widget_type(_canvas)

            _canvas.bind('<Configure>', lambda _e: _canvas.configure(scrollregion=_canvas.bbox("all")))
            _canvas.create_window((0, 0), window=self._widget, anchor="nw")

            self._scrollable_object = _canvas

        # ----------------------------------------------------------------------------------------
        # bind the scrollable object to the scrollbars
        # ----------------------------------------------------------------------------------------

        if self._vsb is not None:
            self._vsb.configure(command=self._scrollable_object.yview)
            self._scrollable_object.configure(yscrollcommand=self._vsb.set)

        if self._hsb is not None:
            self._hsb.configure(command=self._scrollable_object.hview)
            self._scrollable_object.configure(xscrollcommand=self._hsb.set)

    # ==============================================================================================
    # see_widget
    # ==============================================================================================
    def see_widget(self, widget_to_be_seen):
        """ scrolls scrollable object so that widget will be seen"""
        if widget_to_be_seen is None: return

        # make sure idle tasks are finished (includes redrawing of changes in geometry)
        self.update_idletasks()

        # vertical scrolling
        if self._vsb is not None:
            scrollable_object_height = self._widget.winfo_height()
            scrollable_object_top = self.widget.winfo_rooty()

            to_be_seen_top = widget_to_be_seen.winfo_rooty()
            to_be_seen_height = widget_to_be_seen.winfo_height()
            to_be_seen_bottom = to_be_seen_top + to_be_seen_height

            scroll_region_height = self._scrollable_object.winfo_height()
            scroll_region_top = self._scrollable_object.winfo_rooty()
            scroll_region_bottom = scroll_region_top + scroll_region_height

            if to_be_seen_top < scroll_region_top:
                dy = to_be_seen_top - scroll_region_top
                pos = (scroll_region_top - scrollable_object_top + dy) / scrollable_object_height
                self._scrollable_object.yview_moveto(pos)

            if to_be_seen_bottom > scroll_region_bottom:
                dy = to_be_seen_bottom - scroll_region_bottom
                pos = (scroll_region_top - scrollable_object_top + dy) / scrollable_object_height
                self._scrollable_object.yview_moveto(pos)

        if self._hsb is not None:
            eprint("This functionality has not been implemented yet!")