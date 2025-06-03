from __future__ import annotations
from tkinter import *
import tkinter as tk
from tkinter import ttk
from functools import partial
import schedule.Tk as new_tk

import sys
import traceback
from typing import Any, Literal


def eprint(*args, **kwargs):
    print("\n", file=sys.stderr, **kwargs)
    print(*args, file=sys.stderr, **kwargs)
    print(traceback.format_stack()[0], file=sys.stderr, **kwargs)
    exit()


###############
# https://docstore.mik.ua/orelly/perl3/tk/ch06_03.htm
# Section 6.3.8
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/events.html
# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html
###############

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

                        'e' is a vertical scrollbar on the right side of the widget

                        you can only have one scrollbar for horizontal and one for vertical

    all other options will be passed to the widget when it is created


Properties
----------
    widget -> the widget that you asked to be created

    horizontal_scrollbar -> the horizontal scrollbar that was created

    vertical_scrollbar -> the vertical scrollbar that was created

Methods
-------
    see (self,internal_widget)

    yview_moveto(self, fraction)

    xview_moveto(self, fraction)

    yview(self, widget=None)

    xview(self, widget=None)

    yview_scroll(self, number, what)

    xview_scroll(self, number, what)


Notes
-----
    The created object will be a frame, so you can pack or grid it as desired

    To access the scrolled widget, use 'self.widget' property

    To access the scrollbars, use self.horizontal_scrollbar and self.vertical_scrollbar

     - scrollbars have been set_default_fonts_and_colours to not take focus, if you want to
     change that you have to modify
       the scrollbars after the scrolled widget has been created


Examples
--------

example::

        from tkinter import *
        from scrolled import Scrolled

        _mw = Tk()
        scrolled_listbox = Scrolled(_mw, 'Listbox', scrollbars=E, bg='pink')
        scrolled_listbox.pack(fill=BOTH, side=TOP, expand=1)
        scrolled_listbox.vertical_scrollbar.configure(width=30)

        for i in range(20):
            scrolled_listbox.widget.insert("end", f"entry {i=}")

        _mw.mainloop()

    Example
        from tkinter import *
        from scrolled import Scrolled

        _mw = Tk()
        scrolled_frame = Scrolled(_mw, 'Frame', scrollbars=E)
        scrolled_frame.pack(fill=BOTH, side=TOP, expand=1)

        for i in range(10):
            Button(scrolled_frame.widget,text=f"Button {i}").pack(ipady=10)

        _mw.mainloop()
    """

    # ==============================================================================================
    # properties
    # ==============================================================================================
    @property
    def widget(self):
        return self._widget

    @property
    def horizontal_scrollbar(self):
        return self._horizontal_scrollbar

    @property
    def vertical_scrollbar(self):
        return self._vertical_scrollbar

    # ==============================================================================================
    # constructor
    # ==============================================================================================
    def __init__(self, parent, widget_type, scrollbars="e", **kwargs):
        """ constructs scrollbars, widget from widget_type, attaches them appropriately

        a frame will be created (self)
        a widget of widget resource_type will be created inside the frame (self.widget)
        scrollbars will be created as requested (self.horizontal_scrollbar, self.vertical_scrollbar)
        """
        # ----------------------------------------------------------------------------------------
        # initialize_columns the holding frame
        # ----------------------------------------------------------------------------------------
        Frame.__init__(self, parent)

        self._widget_type = widget_type
        self._scrollable_object = None
        self._vertical_scrollbar = None
        self._horizontal_scrollbar = None
        self._widget = None

        # ----------------------------------------------------------------------------------------
        # get_by_id the Tk object that needs to be created
        # ----------------------------------------------------------------------------------------
        _tk_widget_type = None

        # looking for a Tk widget
        try:
            _tk_widget_type = getattr(tk, widget_type)
        except AttributeError:

            # looking for an expanded tk widget from ttk
            try:
                _tk_widget_type = getattr(ttk, widget_type)
            except AttributeError:

                # looking for a personalized widget in schedule.Tk
                try:
                    _tk_widget_type = getattr(new_tk, widget_type)
                except AttributeError as e:
                    eprint(e)

        # ----------------------------------------------------------------------------------------
        # bail out if user is trying to create 2 scrollbars in the same orientation
        # ----------------------------------------------------------------------------------------
        if ('e' in scrollbars and 'w' in scrollbars) or ('n' in scrollbars and 's' in scrollbars):
            eprint(f"You cannot have two horizontal or two vertical scrollbars ({scrollbars=})")

        # ----------------------------------------------------------------------------------------
        # create scrollbars
        # ----------------------------------------------------------------------------------------
        if 'n' in scrollbars or 's' in scrollbars:
            self._horizontal_scrollbar = tk.Scrollbar(self, orient=HORIZONTAL, takefocus=0)
            if 'n' in scrollbars:
                self._horizontal_scrollbar.pack(side=TOP, fill=X)
            else:
                self._horizontal_scrollbar.pack(side=BOTTOM, fill=X)

        if 'e' in scrollbars or 'w' in scrollbars:
            self._vertical_scrollbar = tk.Scrollbar(self, orient=VERTICAL, takefocus=0, troughcolor='pink')
            if 'e' in scrollbars:
                self._vertical_scrollbar.pack(side=RIGHT, fill=Y)
            else:
                self._vertical_scrollbar.pack(side=LEFT, fill=Y)

        # ----------------------------------------------------------------------------------------
        # is the widget we want to scroll, scrollable?
        # ----------------------------------------------------------------------------------------
        try:
            _xview = getattr(_tk_widget_type, "xview")
            _yview = getattr(_tk_widget_type, "yview")

            self._widget = _tk_widget_type(self, **kwargs)
            self._scrollable_object = self._widget
            self._scrollable_object.pack(fill='both', expand=1)

        except AttributeError:

            # ----------------------------------------------------------------------------------------
            # the widget is not scrollable, so we are going to put it inside a canvas object
            # which is scrollable
            # ----------------------------------------------------------------------------------------
            canvas_args = {}
            if 'width' in kwargs:
                canvas_args['width'] = kwargs['width']
            if 'height' in kwargs:
                canvas_args['height'] = kwargs['height']
            _canvas = Canvas(self, **canvas_args)
            _canvas.pack(side=TOP, fill=BOTH, expand=1)

            self._widget = _tk_widget_type(_canvas, **kwargs)

            _canvas.bind('<Configure>', partial(self.update_scrollbars, _canvas))
            _canvas.create_window((0, 0), window=self._widget, anchor="nw")

            self._scrollable_object = _canvas

        # ----------------------------------------------------------------------------------------
        # bind the scrollable object to the scrollbars
        # ----------------------------------------------------------------------------------------

        if self._vertical_scrollbar is not None:
            self._vertical_scrollbar.configure(command=self._scrollable_object.yview)
            self._scrollable_object.configure(yscrollcommand=self._vertical_scrollbar.set)

        if self._horizontal_scrollbar is not None:
            self._horizontal_scrollbar.configure(command=self._scrollable_object.xview)
            self._scrollable_object.configure(xscrollcommand=self._horizontal_scrollbar.set)
        self.pack(fill="both", expand=1)

    # ===============================================================================================================
    # pass on all 'configure' to the scrollable object
    # ===============================================================================================================
    # def configure(self, **kwargs):
    #    self._widget.configure(**kwargs)

    # ===============================================================================================================
    # if adding things to the frame, we need to update the scrollbars.
    # ... at this point must be done manually from the calling code
    # ===============================================================================================================
    def update_scrollbars(self, *_args, **_kwargs):
        """resets the scrollbars to accommodate changes in the canvas size"""
        if isinstance(self._scrollable_object, Canvas):
            canvas = self._scrollable_object
            canvas.configure(scrollregion=canvas.bbox("all"))

    # ===============================================================================================================
    # Subwidget
    # ===============================================================================================================
    def Subwidget(self, name: str) -> Any:
        """returns scrollbar, the widget to be scrolled, or the scrolled object"""
        if name == 'xscrollbar':
            return self._horizontal_scrollbar
        if name == 'yscrollbar':
            return self._vertical_scrollbar
        if name == self._widget_type:
            return self._widget
        if name == 'scrollable':
            return self._scrollable_object

    # ===============================================================================================================
    # scrolling methods
    # ===============================================================================================================
    def see(self, widget, **_kwargs):
        """Adjusts the view so that widget is visible.

        Additional parameters in options-value pairs can be passed,
        each option-value pair must be one of the following

        NOT IMPLEMENTED YET

        -anchor => anchor
        Specifies how to make the widget visible. If not given then as much of the widget as possible is made visable.

        Possible values are n, s, w, e, nw, ne, sw and se.
        This will cause an edge on the widget to be aligned with the corresponding edge on the pane.
        for example nw will cause the top left of the widget to be placed at the top left of the pane.
        s will cause the bottom of the widget to be placed at the bottom of the pane, and as much of
        the widget as possible made visible in the x direction.

        """

        self.xview(widget)
        self.yview(widget)

    def yview_moveto(self, fraction):
        """
            Adjusts the view in the window so that fraction of the total width of the Scrolloable object is off-screen
            to the top.

            fraction must be a fraction between 0 and 1.
        """
        if self._vertical_scrollbar is not None:
            self._scrollable_object.yview_moveto(fraction)

    def xview_moveto(self, fraction):
        """
            Adjusts the view in the window so that fraction of the total width of the Scrolloable object is off-screen
            to the left.

            fraction must be a fraction between 0 and 1.
        """
        if self._horizontal_scrollbar is not None:
            self._scrollable_object.xview_moveto(fraction)

    def xview(self, widget=None):
        """
        No parameters:
            Returns a list containing two elements, both of which are real fractions between 0 and 1.
            The first element gives the position of the left of the window, relative to the scrollable object as a whole
            (0.5 means it is halfway through the Frame, for example).
            The second element gives the position of the right of the window, relative to the scrollable object
            as a whole.

        Tk Widget defined
            Adjusts the view in the window so that widget is displayed.

         """

        # make sure idle tasks are finished (includes redrawing of changes in geometry)
        self.update_idletasks()

        if self.horizontal_scrollbar is None:
            return 0, 1

        if widget is not None:
            # NOT IMPLEMENTED YET
            pass

    def yview(self, widget=None):
        """
        No parameters:
            Returns a list containing two elements, both of which are real fractions between 0 and 1.
            The first element gives the position of the top of the window, relative to the scrollable object as a whole
            (0.5 means it is halfway through the Frame, for example).
            The second element gives the position of the bottom of the window, relative to the scrollable object
            as a whole.

        Tk Widget defined
            Adjusts the view in the window so that widget is displayed.

        """

        # make sure idle tasks are finished (includes redrawing of changes in geometry)
        self.update_idletasks()

        if self.vertical_scrollbar is None:
            return 0, 1  # no scrollbar

        if widget is not None:
            scrollable_object_height = self._widget.winfo_height()
            scrollable_object_top = self.widget.winfo_rooty()

            to_be_seen_top = widget.winfo_rooty()
            to_be_seen_height = widget.winfo_height()
            to_be_seen_bottom = to_be_seen_top + to_be_seen_height

            scroll_region_height = self._scrollable_object.winfo_height()
            scroll_region_top = self._scrollable_object.winfo_rooty()
            scroll_region_bottom = scroll_region_top + scroll_region_height

            if to_be_seen_top < scroll_region_top:
                dy = to_be_seen_top - scroll_region_top
                pos = (scroll_region_top - scrollable_object_top + dy) / scrollable_object_height
                self._scrollable_object.yview_moveto(pos)

            if to_be_seen_bottom > scroll_region_bottom:
                dy = to_be_seen_bottom - scroll_region_bottom + to_be_seen_height
                pos = (scroll_region_top - scrollable_object_top + dy) / scrollable_object_height
                self._scrollable_object.yview_moveto(pos)

        return self.vertical_scrollbar.get()

    def xview_scroll(self, number: int, what: Literal["units", "pages"]) -> None:
        """ Shift the x-view according to NUMBER which is measured in "units" or "pages" (WHAT).

        'what' must be  Literal["units", "pages"]
        """
        if self.vertical_scrollbar is None:
            self._scrollable_object.xview_scroll(number, what)

    def yview_scroll(self, number: int, what: Literal["units", "pages"]) -> None:
        """ Shift the y-view according to NUMBER which is measured in "units" or "pages" (WHAT).

        'what' must be  Literal["units", "pages"]
        """
        if self.vertical_scrollbar is None:
            self._scrollable_object.yview_scroll(number, what)
