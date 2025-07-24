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

def get_conflict_colour_info(resource_type:ResourceType) -> tuple[dict,...]:

    conflict_colour_info = []
    conflict_types = [ConflictType.TIME, ConflictType.LUNCH,
              ConflictType.MINIMUM_DAYS, ConflictType.AVAILABILITY]
    match resource_type:
        case ResourceType.teacher:
            conflict_types.insert(0, ConflictType.TIME_TEACHER)
        case ResourceType.stream:
            conflict_types.insert(0, ConflictType.TIME_STREAM)
        case ResourceType.lab:
            conflict_types.insert(0, ConflictType.TIME_LAB)

    for c in conflict_types:
        bg = ConflictType.colours()[c]
        fg = "white"
        if Colour.is_light(bg):
            fg = "black"
        text = c.name
        conflict_colour_info.append({
            "bg": Colour.string(bg),
            "fg": Colour.string(fg),
            "text": text
        })
    return conflict_colour_info

IMMOVABLE_COLOUR: str = "#dddddd"
