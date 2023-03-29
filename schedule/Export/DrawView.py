"""DrawView - code that draws the View stuff only."""
import re
from tkinter import Canvas

from schedule.PerlLib import Colour
from schedule.Schedule.Block import Block

# region METHODS
edge = 5
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
times: dict[int, str] = {
    8: "8am",
    9: "9am",
    10: "10am",
    11: "11am",
    12: "12pm",
    13: "1pm",
    14: "2pm",
    15: "3pm",
    16: "4pm",
    17: "5pm",
    18: "6pm"
}
earliest_time = min(times.keys())
latest_time = max(times.keys())
lime_green = "#ccffcc"
sky_blue = "#b3e6ff"
blue = Colour.add(sky_blue, sky_blue)
teal = Colour.add(sky_blue, lime_green)

colours: dict[str, str] = {'lab': "#cdefab", 'teacher': "#abcdef", 'stream': teal}


# =================================================================
# draw_background
# =================================================================
def draw_background(canvas: Canvas, scl: dict):
    """Draws the Schedule timetable on the specified canvas.
    Parameters:
        canvas: Canvas to draw on.
        scl: Scaling info [dictionary]."""
    x_offset = scl['xoff']
    y_offset = scl['yoff']
    xorig = scl['xorg']
    yorig = scl['yorg']
    h_stretch = scl['xscl']
    v_stretch = scl['yscl']
    current_scale = scl['scale']

    # Not sure why it's necessary to reassign these values yet, unless they change further down.
    earliest_time = min(times.keys())
    latest_time = max(times.keys())

    # --------------------------------------------------------------------
    # draw hourly lines
    # --------------------------------------------------------------------
    (None, x_max) = _days_x_coords(days, x_offset, xorig, h_stretch)
    (x_min, None) = _days_x_coords(1, x_offset, xorig, h_stretch)

    for time in times.keys():
        # Draw each hour line.
        (y_hour, y_half) = _time_y_coords(time, 0.5, y_offset, yorig, v_stretch)
        canvas.create_line(
            x_min, y_half, x_max, y_hour,
            fill="dark grey",
            dash="-"
        )

        # Hour text.
        canvas.create_text(
            (x_min + xorig) / 2,
            y_hour, text=times[time]
        )

        # for all inner times, draw a dotted line for the half hour.
        if time != latest_time:
            canvas.create_line(
                x_min, y_half, x_max, y_hour,
                fill="grey",
                dash="."
            )

        # Half-hour text. NOTE: Font size supposedly too big in original perl version of the code.
        canvas.create_text(
            (x_min + xorig) / 2,
            y_half, text=":30"
        )

    # --------------------------------------------------------------------
    # draw day lines
    # --------------------------------------------------------------------
    (y_min, y_max) = _time_y_coords(
        earliest_time, (latest_time - earliest_time),
        y_offset, yorig, v_stretch
    )

    for i in range(len(days) + 1):
        (x_day, x_day_end) = _days_x_coords(i + 1, x_offset, xorig, h_stretch)
        canvas.create_line(x_day, yorig, x_day, y_max)

        # day text
        if i < len(days):
            if current_scale <= 0.5:
                canvas.create_text(
                    (x_day + x_day_end) / 2,
                    (y_min + yorig) / 2,
                    text=days[i][0:1]
                )
            else:
                canvas.create_text(
                    (x_day + x_day_end) / 2,
                    (y_min + yorig) / 2,
                    text=days[i]
                )

# =================================================================
# get_block_text
# =================================================================
#Todo: Implement the ViewType enum in some capacity.
def get_block_text(block: Block, scale: float = 1, type = "teacher"):
    """Get the text for a specific type of block.

    Parameters:
        block: A Block object.
        scale: scale (1 = 100%)
        type: Type of view [teacher|block|stream (affects what gets drawn on the block)."""
    # --------------------------------------------------------------------
    # get needed block information
    # --------------------------------------------------------------------
    block_num = block.section.course.number
    block_sec = f"({block.section.number})"
    block_section_name = block.section.title
    labs = block.labs()
    block_lab = ",".join(labs)
    block_duration = block.duration
    block_start_time = block.start_number
    streams = block.section.streams
    block_streams = ",".join(streams)

    # If teacher name is too long, split into multiple lines.
    teachers = block.teachers()
    block_teacher = ""
    for t in teachers:
        name = str(t)
        if len(name) > 15:
            block_teacher = block_teacher + "\n".join(name.split()) + "\n"
        else:
            block_teacher = block_teacher + f"{str(t)}\n"
    block_teacher = block_teacher.rstrip()

    # --------------------------------------------------------------------
    # The diagram has been scaled down,
    # ... change what gets printed on the block
    # --------------------------------------------------------------------
    if scale <= 0.75:
        # -----------------------------------------------------------
        # course (scale < .75)
        # -----------------------------------------------------------
        # remove program number from course number (i.e. 420-506 becomes 506)
        if scale == 0.5:
            block_num = re.split("[-*]", block_num)

        # -----------------------------------------------------------
        # teachers (scale < .75)
        # -----------------------------------------------------------
        block_teacher = ""

        # Don't add teachers if this is a teacher view.
        if type is not "teacher":
            for t in teachers:
                block_teacher = block_teacher + ", ".join(map(t.firstname[0:1], t.lastname[0:1]))

                # add ellipsis to end of teacher string as necessary
                if scale == 0.5 and len(teachers) >=3:
                    block_teacher = block_teacher[0:7] + "..."
                elif len(teachers) >= 4:
                    block_teacher = block_teacher[0:11] + "..."

        # -----------------------------------------------------------
        # labs/resources (scale < .75)
        # -----------------------------------------------------------
        block_lab = ""
        if type is not "lab":
            block_lab = ", ".join(map(lambda l: l.number, labs))

            # add ellipsis to end of lab string as necessary
            if scale == 0.5 and len(labs) >= 3:
                block_lab = block_lab[0:7] + "..."
            elif len(labs) >= 4:
                block_lab = block_lab[0:11] + "..."

        # -----------------------------------------------------------
        # streams (scale < .75)
        # -----------------------------------------------------------
        block_streams = ""

        # only add stream/text if no teachers or labs,
        # or GuiBlock can fit all info (i.e. duration of 2 hours or more)
        if type is not "stream" or block_duration >= 2:
            block_streams = ", ".join(map(lambda s: s.number, streams))

            # add ellipsis to end of stream as necessary.
            if scale == 0.5 and len(streams) >= 3:
                block_streams = block_streams[0:7] + "..."
            elif len(streams) >= 4:
                block_streams = block_streams[0:11] + "..."

    # --------------------------------------------------------------------
    # define what to display
    # --------------------------------------------------------------------

    block_text = f"{block_num}\n{block_section_name}\n"
    if type is not "teacher" and block_teacher:
        block_text += f"{block_teacher}\n"
    if type is not "lab" and block_lab:
        block_text += f"{block_lab}\n"
    if type is not "stream" and block_streams:
        block_text += f"{block_streams}\n"
    block_text = block_text.rstrip()

    return block_text
# endregion
