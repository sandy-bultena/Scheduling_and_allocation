from GUI.MainPageBaseTk import MainPageBaseTk
from PerlLib import Colour
from tkinter import Label, StringVar, Frame, Button
from functools import partial

open_button: Button                      # button used to open selected files
schedules: dict[str, int] = {}           # selected schedules
short_scheds: dict[str, StringVar] = {}  # short names of selected schedules
short_sched_name: int = 30               # max length of schedule name displayed to user
semesters: list[str] = []                # array of semesters


class AllocationManagerTk(MainPageBaseTk):
    def create_front_page(self, preferences, semesters_, open_schedules_callback, select_schedule_callback):
        from Tk import FindImages

        global semesters, open_button
        semesters = semesters_

        logo_file = FindImages.get_allocation_logo()
        option_frame = super().create_front_page(logo_file)

        button_width = 100  # double Perl version

        disabled_colour = Colour.string(self.colours['DataBackground'])
        if Colour.is_light(disabled_colour):
            disabled_colour = Colour.darken(disabled_colour, 20)
        else:
            Colour.lighten(disabled_colour, 20)

        # --------------------------------------------------------------
        # selected files
        # --------------------------------------------------------------
        Label(option_frame, text="Selected Schedules", font=self.fonts['bigbold'], bg=self.colours['DataBackground'])\
            .pack(side='top', fill='x', expand=0)

        for semester in semesters:
            if semester not in short_scheds:
                short_scheds[semester] = StringVar()

            Label(option_frame, textvariable=short_scheds[semester], bg=self.colours['DataBackground'])\
                .pack(side='top', fill='x', expand=0)

        Label(option_frame, text='\n', font=self.fonts['bigbold'], bg=self.colours['DataBackground'])\
            .pack(side='top', fill='x', expand=0)

        # --------------------------------------------------------------
        # choose schedules
        # --------------------------------------------------------------
        (choose_frame := Frame(option_frame)).pack(side='top', fill='x', expand=0)

        for i, semester in enumerate(semesters):
            Label(choose_frame, text=semester.capitalize() + ":",
                  bg=self.colours['DataBackground'], font=self.fonts['bold'])\
                .grid(row=i, column=0, sticky='nsew', columnspan=2)

            def _open_button(_semester):
                sched = select_schedule_callback(_semester)
                if sched:
                    _set_file(_semester, sched.id, sched.descr)

            Button(choose_frame, text='Open Schedule', font=self.fonts['normal'], borderwidth=0, height=3,
                   bg=self.colours['DataBackground'], command=partial(_open_button, semester))\
                .grid(row=i, column=2, columnspan=2, sticky='nsew')

        # --------------------------------------------------------
        # gui layout commands
        # --------------------------------------------------------
        columns, rows = choose_frame.grid_size()
        for i in range(columns):
            choose_frame.grid_columnconfigure(i, weight=1)
        choose_frame.grid_rowconfigure(rows - 1, weight=1)

        Frame(option_frame, bg=self.colours['DataBackground']).pack(expand=0, fill='x')

        # --------------------------------------------------------------
        # make button for opening selected schedules
        # --------------------------------------------------------------
        text = 'Open Selected Schedules'
        open_button = Button(option_frame,
                             text=text,
                             font=self.fonts['big'],
                             borderwidth=0,
                             bg=self.colours['DataBackground'],
                             command=open_schedules_callback,
                             width=button_width,
                             height=3,
                             disabledforeground=disabled_colour)
        open_button.pack(side='top', fill='x', expand=0)

        # --------------------------------------------------------------
        # set selected schedules to those in the preference file
        # --------------------------------------------------------------
        for semester in semesters:
            _set_file(semester, preferences.get(f'current_{semester}_id'), preferences.get(f'current_{semester}_name'))


def _set_file(semester, schedule_id, schedule_name):
    if schedule_id is None or schedule_name is None:
        _all_files_chosen()
        return
    if semester not in short_scheds:
        short_scheds[semester] = StringVar()

    schedules[semester] = schedule_id
    # limit to the last 30 or fewer characters
    display = schedule_name[-short_sched_name:len(schedule_name)]
    if len(schedule_name) > short_sched_name:
        display = f"(...) {display}"
    short_scheds[semester].set(display)

    _all_files_chosen()


def _all_files_chosen():
    enable_flag = "normal"
    for semester in semesters:
        if semester not in schedules:
            enable_flag = 'disabled'
    open_button.configure(state=enable_flag)
