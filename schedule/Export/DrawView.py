"""DrawView - code that draws the View stuff only."""
import re
from tkinter import Canvas

from schedule.PerlLib import Colour
from schedule.Schedule.Block import Block

"""SYNOPSIS
    
    from tkinter import *
    from tkinter import ttk
    
    from schedule.Export import DrawView
    from schedule.Schedule.Teacher import Teacher
    from schedule.Schedule.Block import Block
    from schedule.Schedule.ScheduleEnums import WeekDay
    from schedule.Schedule.database import PonyDatabaseConnection
    from schedule.Schedule.database.db_constants import *

    # ----------------------------------------------------------
    # connect to the database, instantiate a Teacher and some Blocks.
    # ----------------------------------------------------------
    db = PonyDatabaseConnection.define_database(host=HOST, db=DB_NAME, user=USERNAME,
                                                        passwd=PASSWD, provider=PROVIDER)

    teacher = Teacher("John", "Smith")
    block_1 = Block(WeekDay.Monday, "8:30", 1.5, 1)
    block_2 = Block(WeekDay.Wednesday, "8:30", 1.5, 1)
    block_1.assign_teacher(teacher)
    block_2.assign_teacher(teacher)

    blocks = [block_1, block_2]

    # ----------------------------------------------------------
    # Create the Tk main window and the canvas
    # ----------------------------------------------------------
    main_window = Tk()
    main_window.geometry('500x600-300-40')
    cn = Canvas(main_window)
    cn.pack(fill=BOTH, expand=True)

    # ----------------------------------------------------------
    # Define what scale you want
    # ----------------------------------------------------------
    scl = {
        'xoff': 1,
        'yoff': 1,
        'xorg': 0,
        'yorg': 0,
        'xscl': 100,
        'yscl': 60,
        'scale': 1
    }

    # ----------------------------------------------------------
    # draw the grid on the canvas.
    # ----------------------------------------------------------
    DrawView.draw_background(cn, scl)

    # ----------------------------------------------------------
    # Draw the teacher blocks on canvas. 
    # Set the type argument to "lab" or "teacher" to change the
    # colours and the information that is displayed in the 
    # block.
    # ----------------------------------------------------------
    for block in blocks:
        DrawView.draw_block(cn, block, scl, "stream")
    main_window.mainloop()

"""

# TODO: Make this into a static class?

# region METHODS
Edge = 5
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
    (dummy_x, x_max) = _days_x_coords(len(days), x_offset, xorig, h_stretch)
    (x_min, dummy_y) = _days_x_coords(1, x_offset, xorig, h_stretch)

    for time in times.keys():
        # Draw each hour line.
        (y_hour, y_half) = _time_y_coords(time, 0.5, y_offset, yorig, v_stretch)
        canvas.create_line(
            x_min, y_hour, x_max, y_hour,
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
                x_min, y_half, x_max, y_half,
                fill="grey",
                dash="."
            )

            # Half-hour text. NOTE: Font size supposedly too big in original perl version of the
            # code.
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
# Todo: Implement the ViewType enum in some capacity.
def get_block_text(block: Block, scale: float = 1, type="teacher"):
    """Get the text for a specific type of block.

    Parameters:
        block: A Block object.
        scale: scale (1 = 100%)
        type: Type of view [teacher|lab|stream (affects what gets drawn on the block)."""
    # --------------------------------------------------------------------
    # get needed block information
    # --------------------------------------------------------------------
    # These checks prevent the app from crashing if the Block doesn't have an associated Section.
    block_num = block.section.course.number if block.section else ""
    block_sec = f"({block.section.number})" if block.section else ""
    block_section_name = block.section.title if block.section else ""
    labs = block.labs()
    block_lab = ",".join(labs)
    block_duration = block.duration
    block_start_time = block.start_number
    streams = block.section.streams if block.section else ()
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
        if type != "teacher":
            for t in teachers:
                block_teacher = block_teacher + ", ".join(map(t.firstname[0:1], t.lastname[0:1]))

                # add ellipsis to end of teacher string as necessary
                if scale == 0.5 and len(teachers) >= 3:
                    block_teacher = block_teacher[0:7] + "..."
                elif len(teachers) >= 4:
                    block_teacher = block_teacher[0:11] + "..."

        # -----------------------------------------------------------
        # labs/resources (scale < .75)
        # -----------------------------------------------------------
        block_lab = ""
        if type != "lab":
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
        if type != "stream" or block_duration >= 2:
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
    if type != "teacher" and block_teacher:
        block_text += f"{block_teacher}\n"
    if type != "lab" and block_lab:
        block_text += f"{block_lab}\n"
    if type != "stream" and block_streams:
        block_text += f"{block_streams}\n"
    block_text = block_text.rstrip()

    return block_text


# =================================================================
# draw_block
# =================================================================
def draw_block(canvas: Canvas, block, scl: dict, type,
               colour=None, edge=None, block_tag: int = None) -> dict | None:
    """Draws the Schedule timetable on the specified canvas.

    Parameters:
        canvas: Canvas to draw on.
        block: Block object.
        scl: Scaling info [dictionary].
        type: Type of view [teacher|block|stream] (affects what gets drawn on the block).
        colour: colour of block.
        block_tag: Integer used to give the drawn block a unique tag identifier.

    Returns:
        -A dict containing the following keys:
        -lines: a list of canvas line objects.
        -text: text printed on the block.
        -coords: array of canvas coordinates for the block.
        -rectangle: the canvas rectangle object.
        -colour: the colour of the block."""
    scale = scl['scale']
    if not block:
        return

    # --------------------------------------------------------------------
    # set the colour and pixel width of edge
    # --------------------------------------------------------------------
    if not colour:
        colour = colours[type] or colours['teacher']

    global Edge

    if edge is None:
        edge = Edge
    Edge = edge

    colour = Colour.string(colour)

    # --------------------------------------------------------------------
    # get coords
    # --------------------------------------------------------------------
    coords = get_coords(block.day_number, block.start_number, block.duration, scl)

    # --------------------------------------------------------------------
    # get needed block information
    # --------------------------------------------------------------------
    block_text = get_block_text(block, scale, type)

    # --------------------------------------------------------------------
    # draw the block
    # --------------------------------------------------------------------
    # Create a rectangle.
    rectangle = canvas.create_rectangle(coords, fill=colour, outline=colour,
                                        tags=("rectangle", "members"))
    if block_tag:
        canvas.addtag_withtag(f"rectangle_block_{block_tag}", "rectangle")

    # shade edges of guiblock rectangle
    lines = []
    (x1, y1, x2, y2) = coords
    (light, dark, text_colour) = get_colour_shades(colour)
    for i in range(0, edge - 1):
        lines.append(
            canvas.create_line(x2 - i, y1 + i, x2 - i, y2 - i, x1 + i, y2 - i, fill=dark[i],
                               tags="lines")
        )
        lines.append(
            canvas.create_line(
                x2 - i, y1 + i, x1 + i, y1 + i, x1 + i, y2 - i, fill=light[i], tags="lines"
            )
        )
    if block_tag:
        canvas.addtag_withtag(f"lines_block_{block_tag}", "lines")

    # set text
    text = canvas.create_text(
        (x1 + x2) / 2, (y1 + y2) / 2, text=block_text, fill=text_colour,
        tags=("text", "members")
    )

    if block_tag:
        canvas.addtag_withtag(f"text_block_{block_tag}", "text")

    # group rectangle and text to create a guiblock,
    # so that they both move as one on UI
    # NOTE: createGroup is specific to the Perl/Tk version of the canvas widget. Need a workaround
    # for this.
    # group = canvas.create_g

    return {
        'lines': lines,
        'text': text,
        'coords': coords,
        'rectangle': rectangle,
        'colour': colour
    }


# =================================================================
# coords_to_day_time_duration
# =================================================================
def coords_to_day_time_duration(x, y, y2, scl: dict):
    """Determines the day, start time, and duration based on canvas coordinates.

    Parameters:
        x: x position (determines day).
        y: y1 position (determines start).
        y2: y2 position (determines duration).
        scl: Scaling info [dictionary]."""
    day = x / scl['xscl'] - scl['xoff'] - scl['xorg']
    time = y / scl['yscl'] - scl['yoff'] + earliest_time - scl['yorg']
    duration = (y2 + 1 - y) / scl['yscl']

    return day, time, duration


# =================================================================
# get_coords
# =================================================================
def get_coords(day, start, duration, scl):
    """Determines the canvas coordinates based on day, start time, and duration.

    Parameters:
        day: day of week (1 = Monday)
        start: start time (24-hour clock)
        scl: Scaling info [dictionary]"""
    (x, x2) = _days_x_coords(day, scl['xoff'], scl['xorg'], scl['xscl'])
    (y, y2) = _time_y_coords(start, duration, scl['yoff'], scl['yorg'], scl['yscl'])

    return x, y, x2, y2


# =================================================================
# get the shades of the colour
# =================================================================

def get_colour_shades(colour: str):
    """Get the shades of the passed colour.

    Parameters:
        colour: A hexadecimal colour code.

    Returns:
        Array of colours lighter than passed colour
        Array of colours darker than passed colour
        Recommended colour for text if overlaid on colour"""
    edge = Edge

    # convert colour to hue, saturation, and light.
    (h, s, l) = Colour.hsl(colour)

    # Calculate the light/dark changes.
    # light_intensity = l > .7 ? (1 - l) * 75 : 30 * .75
    light_intensity = (1 - l) * 75 if l > .7 else 30 * .75
    dark_intensity = l * 75 if l < .3 else 30 * .75

    # recommended text colour
    textcolour = "black"
    if not Colour.is_light(colour):
        textcolour = "white"

    # create a light/dark gradient of colours.
    light = []
    dark = []

    for i in range(edge - 1):
        l_factor = (1 - (i / edge)) * light_intensity
        d_factor = (1 - (i / edge)) * dark_intensity
        light.append(Colour.lighten(colour, l_factor))
        dark.append(Colour.darken(colour, d_factor))

    # Return info.
    return light, dark, textcolour


# =================================================================
# using scale info, get the y limits for a specific time period
# =================================================================
def _time_y_coords(start, duration, y_offset, yorig, v_stretch):
    """using scale info, get the y limits for a specific time period."""
    y_offset = y_offset * v_stretch + yorig
    y = y_offset + (start - earliest_time) * v_stretch
    y2 = duration * v_stretch + y - 1

    return y, y2


# =================================================================
# using scale info, get the x limits for a specific day
# =================================================================
def _days_x_coords(day: int, x_offset, xorig, h_stretch):
    x_offset = x_offset * h_stretch + xorig
    x = x_offset + (day - 1) * h_stretch
    x2 = x_offset + (day) * h_stretch - 1

    return x, x2


# endregion

"""
Canvas Requirements

This code draws on a generic canvas.  

The interface to this canvas follows a subset of the Tk->canvas methods.  For a
more detailed list of what the various options means, check the Tk manuals online.

It must follow these rules:

=head2 Coordinates

The coordinate system of the canvas is the same as the Tk coordinate system,
where the origin (0,0) is the top left corner, and 'y' increases as it goes 
down the page.

=head2 createLine

B<Parameters>

=over

=item * C<x1,y1,x2,y2,> coordinates of the start and stop position of the line

=item * C<< -fill => "colour", >> the colour of the line (OPTIONAL... default is "black"),

=item * C<< -dash => "dash string" >> the type of dash line (OPTIONAL ... default is no dash)

=back

B<Returns>

A canvas CreateLine object


"""

"""
Adapted to Python by Evan Laverdiere
"""
