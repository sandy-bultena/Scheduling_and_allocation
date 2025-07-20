import re
from schedule.model import Block, ResourceType
from schedule.gui_pages.view_canvas_tk import ViewCanvasTk
from schedule.Utilities.id_generator import IdGenerator

class GuiBlock:
    """GuiBlock - describes the visual representation of a Block."""

    gui_block_ids = IdGenerator()


    # =================================================================
    # new
    # =================================================================
    def __init__(self, block: Block, resource_type: ResourceType, colour:str):
        """
        Creates a gui-usable representation of the block.
        :param view_gui: The context where this block is drawn
        :param block: the block object that needs to be drawn
        :param resource_type: what type of resource is this gui block representing
        :param colour: the default colour of this block
        """
        self._id: int = GuiBlock.gui_block_ids.get_new_id()
        self.block = block
        self.start_time: float = block.time_slot.time_start.hours
        self.day: int = block.time_slot.day.value
        self.duration: float = block.time_slot.duration
        self.resource_type: ResourceType = resource_type

        self.gui_tag = f'gui_tag_{self._id}'

        self.co_ords: list[int] = [0,0,0.0]
        self._colour = colour

    # =================================================================
    # getters/setters
    # =================================================================
    @property
    def colour(self):
        return self._colour

    # =================================================================
    # get_block_text
    # =================================================================
    def get_block_text(self, scale):
        """Get the text for a specific resource_type of blocks"""

        block = self.block
        resource_type = self.resource_type

        # course & section & streams
        course_number = ""
        section_number = ""
        stream_numbers = ""
        if block.section:
            course_number = block.section.course.number if scale > 0.5 else re.split("[-*]", block.section.course.number)
            section_number = block.section.title
            stream_numbers = ",".join((stream.number for stream in block.section.streams()))

        # labs
        lab_numbers = ",".join(l.number for l in block.labs())
        lab_numbers = lab_numbers if scale > .75 else lab_numbers[0:11] + "..."
        lab_numbers = lab_numbers if scale > .50 else lab_numbers[0:7] + "..."
        lab_numbers = lab_numbers if resource_type != ResourceType.lab and scale > .75 else ""

        # streams
        stream_numbers = stream_numbers if scale > .75 else stream_numbers[0:11] + "..."
        stream_numbers = stream_numbers if scale > .50 else stream_numbers[0:7] + "..."
        stream_numbers = stream_numbers if resource_type != ResourceType.stream and scale > .75 else ""

        # teachers
        teachers_name = ""
        for t in block.teachers():
            if len(str(t)) > 15:
                teachers_name = teachers_name + f"{t.firstname[0:1]} {t.lastname}\n"
            else:
                teachers_name = teachers_name + f"{str(t)}\n"
        teachers_name = teachers_name.rstrip()
        teachers_name = teachers_name if scale > .75 else teachers_name[0:11] + "..."
        teachers_name = teachers_name if scale > .50 else teachers_name[0:7] + "..."
        teachers_name = teachers_name if resource_type != ResourceType.stream and scale > .75 else ""


        # --------------------------------------------------------------------
        # define what to display
        # --------------------------------------------------------------------
        block_text = f"{course_number}\n{section_number}\n"
        block_text = block_text + teachers_name + "\n" if teachers_name else block_text
        block_text = block_text + lab_numbers + "\n" if lab_numbers else block_text
        block_text = block_text + stream_numbers + "\n" if stream_numbers else block_text

        block_text = block_text.rstrip()
        return block_text


# =================================================================
# footer
# =================================================================
"""
=head1 AUTHOR

Sandy Bultena, Ian Clement, Jack Burns

Rewritten for Python by Evan Laverdiere

=head1 COPYRIGHT

Copyright (c) 2016, Jack Burns, Sandy Bultena, Ian Clement. 

All Rights Reserved.

This module is free software. It may be used, redistributed
and/or modified under the terms of the Perl Artistic License

     (see http://www.perl.com/perl/misc/Artistic.html)

=cut

1;

"""
