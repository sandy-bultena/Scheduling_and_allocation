from ..Export import DrawView

class View:
    """View - describes the visual representation of a Schedule."""

    # =================================================================
    # global and package variables
    # =================================================================
    undo_number = ""
    redo_number = ""
    clicked_block = 0
    days = DrawView.days
    times = DrawView.times
    earliest_time = min(times.keys())
    latest_time = max(times.keys())
    max_id = 0

