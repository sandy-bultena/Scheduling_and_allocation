
from GUI.AllocationGridTk import AllocationGridTk
from GUI.FontsAndColoursTk import FontsAndColoursTk
from Tk.scrolled import Scrolled


class EditAllocationTk:
    fonts = None

    def __init__(self, frame : Scrolled, allocation_info):
        self.frame = frame
        self.semesters = dict()

        EditAllocationTk.fonts = FontsAndColoursTk.fonts

        self.scrolled_frame = Scrolled(frame, 'Frame')
        self.scrolled_frame.pack(side='top', expand=1, fill='both')

        # scrolled is set_default_fonts_and_colours up, use the internal frame from now on
        self.scrolled_frame = self.scrolled_frame.widget

        # manage the scrollbar?
        # TODO: Determine is this is important

        self.redraw(allocation_info)

    def redraw(self, allocation_info, panes = None):
        if panes is None:
            panes = {}

        for semester_info in allocation_info:
            semester = semester_info['semester']

            # ----------------------------------------------------------------
            # create an allocation grid for this semester,
            # if and only if it is different from the previous grid drawn
            # ----------------------------------------------------------------
            if not self.gui_grid(semester) and self._has_grid_size_changed(
                    semester,
                    semester_info['rows'],
                    semester_info['columns_numbers'],
                    semester_info['totals_numbers']
                    ):
                sem = semester_info['semester']

                # make new frame if it does not already exist
                if sem not in panes or not panes[sem]:
                    panes[sem] = Scrolled(self.scrolled_frame, 'Frame')
                    panes[sem].pack_forget()  # unpack the widget until we're ready to set_default_fonts_and_colours it up

                # make and replace existing grid
                if self.gui_grid(sem):
                    self.gui_grid(sem).delete()

                grid = AllocationGridTk(
                    panes[sem],
                    semester_info['rows'],
                    semester_info['columns_numbers'],
                    semester_info['totals_numbers'],
                    EditAllocationTk.fonts
                )

                # save info for later
                self.gui_grid(sem, grid)
                self.num_rows(sem, semester_info['rows'])
                self.sub_section_numbers(sem, semester_info['columns_numbers'])
                self.total_numbers(sem, semester_info['totals_numbers'])

        # ------------------------------------------------------------------------
        # layout the top widgets via grid manager
        # ------------------------------------------------------------------------
        # now that the grids are drawn, display the semester
        row = 0
        for semester_info in allocation_info:
            sem = semester_info['semester']
            if sem in panes and panes[sem]:
                panes[sem].grid(row=row, sticky='nswe', column=0)
                self.scrolled_frame.grid_rowconfigure(row, weight=0)
                row += 1

        self.scrolled_frame.grid_columnconfigure(0, weight=1)

    # ============================================================================
    # has the grid size changed since last time we created it?
    # ============================================================================
    def _has_grid_size_changed(self, semester, rows, col_nums, tot_nums):
        # number of rows that have changed?
        if rows != self.num_rows(semester):
            return True

        # foreach course, is the number of courses the same,
        # is the number of sections per course the same?

        if len(col_nums) != self.sub_section_numbers(semester):
            return True

        for i, sec in enumerate(col_nums):
            if sec != self.sub_section_numbers(semester)[sec]:
                return True

        if len(tot_nums) != self.total_numbers(semester):
            return True

        for i, total_secs in enumerate(tot_nums):
            if total_secs != self.total_numbers(semester)[i]:
                return True

        return False

    # ============================================================================
    # set_default_fonts_and_colours the allocation grid data_entry_handler callback for specified semester
    # ============================================================================
    def set_cb_data_entry(self, semester, handler):
        self.gui_grid(semester).data_entry_handler(handler)

    # ============================================================================
    # set_default_fonts_and_colours the allocation grid process_data_change_handler callback for specified semester
    # ============================================================================
    def set_cb_process_data_change(self, semester, handler):
        self.gui_grid(semester).process_data_change_handler(handler)

    # ============================================================================
    # set_default_fonts_and_colours the allocation grid bottom_row_ok_handler callback for specified semester
    # ============================================================================
    def set_cb_bottom_row_ok(self, semester, handler):
        self.gui_grid(semester).bottom_row_ok_handler(handler)

    # ============================================================================
    # bind all the data to the various AllocationGrid entry widgets
    # ============================================================================
    def bind_data_to_grid(self, semester, courses_text, courses_balloon,
                          sections_text, teachers_text, bound_data_vars,
                          totals_header, totals_txt, bound_totals,
                          remaining_text, bound_remaining_hours):
        self.gui_grid(semester).populate(
            courses_text,  courses_balloon, sections_text,
            teachers_text, bound_data_vars, totals_header,
            totals_txt,    bound_totals,    remaining_text,
            bound_remaining_hours
        )

    # ============================================================================
    # returns the AllocationGrid for the specific semester
    # ============================================================================
    def gui_grid(self, semester, gui = None):
        if semester not in self.semesters:
            self.semesters[semester] = dict()

        if 'gui_grid' not in self.semesters[semester]:
            self.semesters[semester]['gui_grid'] = None

        if gui:
            self.semesters[semester]['gui_grid'] = gui

        return self.semesters[semester]['gui_grid']

    # ============================================================================
    # number of rows for the allocation grid for a specific semester
    # ============================================================================
    def num_rows(self, semester, *rows):
        if semester not in self.semesters:
            self.semesters[semester] = dict()

        if 'num_rows' not in self.semesters[semester]:
            self.semesters[semester]['num_rows'] = None

        if len(rows):
            self.semesters[semester]['num_rows'] = rows

        return self.semesters[semester]['num_rows']

    # ============================================================================
    # number of section numbers for each course for the allocation grid for a specific semester
    # ============================================================================
    def sub_section_numbers(self, semester, *ssn):
        if semester not in self.semesters:
            self.semesters[semester] = dict()

        if 'sub_section_numbers' not in self.semesters[semester]:
            self.semesters[semester]['sub_section_numbers'] = None

        if len(ssn):
            self.semesters[semester]['sub_section_numbers'] = ssn

        return self.semesters[semester]['sub_section_numbers']

    # ============================================================================
    # number of sub sections for 'totals' heading
    # for the allocation grid for a specific semester
    # ============================================================================
    def total_numbers(self, semester, *tn):
        if semester not in self.semesters:
            self.semesters[semester] = dict()

        if 'total_numbers' not in self.semesters[semester]:
            self.semesters[semester]['total_numbers'] = None

        if len(tn):
            self.semesters[semester]['total_numbers'] = tn

        return self.semesters[semester]['total_numbers']
