from dataclasses import dataclass
from tkinter import *

from TestsAndExamples.gui.dragging_in_canvas import gui_block_is_moving, gui_block_has_stopped_moving
from schedule.Tk import MenuItem, MenuType
from schedule.Utilities import Colour
from schedule.gui_pages.view_dynamic_tk import ViewDynamicTk
from schedule.model import ResourceType, ConflictType

mw = Tk()
cn = Canvas(mw, height=700, width=700, background="white")
cn.pack()


@dataclass
class ExampleBlock:
    start_time: float = 8.0
    day: int = 1
    duration: float = 1.5
    resource_type: ResourceType = ResourceType.teacher
bl1 = ExampleBlock()
bl2 = ExampleBlock(start_time=9.5, day=1)

conflict_info = []
for c in (ConflictType.TIME_TEACHER, ConflictType.TIME, ConflictType.LUNCH,
          ConflictType.MINIMUM_DAYS, ConflictType.AVAILABILITY):
    bg = ConflictType.colours()[c]
    fg = "white"
    if Colour.is_light(bg):
        fg = "black"
    text = c.name
    conflict_info.append({
        "bg": Colour.string(bg),
        "fg": Colour.string(fg),
        "text": text
    })

def refresh_block_handler(view):
    view.draw_block(ResourceType.teacher, 2, 9.5, 3, "Block 1", "bl1")
    print("called refresh block")

def default_menu(*_) -> list[MenuItem]:
    menu1 = MenuItem(name="nothing", label="nothing", menu_type=MenuType.Command, command=lambda: None)
    menu2 = MenuItem(name="more nothing", label="nothing", menu_type=MenuType.Command, command=lambda: None)
    return [menu1, menu2]

view = ViewDynamicTk(mw, "View",conflict_info,
                     refresh_blocks_handler = refresh_block_handler,
                     get_popup_menu_handler=default_menu,
                     on_closing_handler=lambda *_: print ("on closing"),
                     undo_handler=lambda *_: print("undo"),
                     redo_handler=lambda *_: print("redo"),
                     double_click_block_handler=lambda x,*_: print("double clicked",x),
                     gui_block_is_moving_handler= lambda x, *_: print("moving",x),
                     gui_block_has_dropped_handler = lambda x, *_: print("dropped", x),

                     )

view.draw_block(ResourceType.teacher, 2, 9.5, 3, "Block 1", "bl1")

mw.mainloop()