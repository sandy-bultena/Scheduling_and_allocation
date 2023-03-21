from __future__ import annotations
from Schedule.Schedule import Schedule

class Scenario():
    def __init__(self, semester : str = "", status : str = "", description : str = "", schedules = list[Schedule] | None):
        self.semester = semester
        self.status = status
        self.description = description
        self.schedules = schedules if schedules else []