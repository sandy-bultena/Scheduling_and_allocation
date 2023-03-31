from __future__ import annotations
from .Schedule import Schedule

class Scenario():
    def __init__(self, semester : str = "", status : str = "", description : str = "", schedules : set[Schedule] = None):
        self.semester = semester
        self.status = status
        self.description = description
        self.schedules = set(schedules) if schedules else set()