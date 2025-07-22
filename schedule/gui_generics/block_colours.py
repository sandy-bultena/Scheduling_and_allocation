from schedule.Utilities import Colour
from schedule.model import ResourceType, ConflictType

LIME_GREEN = "#ccffcc"
SKY_BLUE = "#b3e6ff"
TEAL = Colour.add(SKY_BLUE, LIME_GREEN)

RESOURCE_COLOURS: dict[ResourceType, str] = {
    ResourceType.lab: "#cdefab",
    ResourceType.teacher: "#abcdef",
    ResourceType.stream: TEAL
}

CONFLICT_COLOUR_INFO = []
for c in (ConflictType.TIME_TEACHER, ConflictType.TIME, ConflictType.LUNCH,
          ConflictType.MINIMUM_DAYS, ConflictType.AVAILABILITY):
    bg = ConflictType.colours()[c]
    fg = "white"
    if Colour.is_light(bg):
        fg = "black"
    text = c.name
    CONFLICT_COLOUR_INFO.append({
        "bg": Colour.string(bg),
        "fg": Colour.string(fg),
        "text": text
    })

IMMOVABLE_COLOUR: str = "#dddddd"
