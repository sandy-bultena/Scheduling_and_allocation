from __future__ import annotations
from .Schedule import Schedule

class Scenario():
    def __init__(self, id, name : str = "", semester : str = "", status : str = "", description : str = "", schedules : set[Schedule] = None):
        self._id = id
        self.name = name
        self.semester = semester
        self.status = status
        self.description = description
        self.schedules = set(schedules) if schedules else set()
    
    @property
    def id(self) -> int:
        """Get the Scenario ID"""
        return self._id
    
    def __str__(self):
        return f"{self.id}: {self.name} ({self.semester}): {self.description} | Status: {self.status}"