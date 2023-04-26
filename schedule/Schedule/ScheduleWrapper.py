from __future__ import annotations

from .Schedule import Schedule
from .Teacher import Teacher
from .Course import Course
from .Lab import Lab
from .Stream import Stream
from .Block import Block
from .Section import Section
from .LabUnavailableTime import LabUnavailableTime
from .Conflict import Conflict
from .Scenario import Scenario

from .database import PonyDatabaseConnection as db
from pony.orm import *

class ScheduleWrapper():
    def __init__(self):
        self.schedules : dict[str, Schedule.Schedule] = dict() # key representing the schedule's semester, ie fall or winter (for allocation manager)
        # if it's not already done, populate the local top-level model classes
        if len(Course.list()) + len(Lab.list()) + len(Stream.list()) + len(Teacher.list()) == 0:
            try:
                ScheduleWrapper.read_DB()
            # DB probably isn't connected yet, just pass
            except ERDiagramError:
                pass
    
    def load_schedule(self, sid : int, semester : str):
        """ Load a schedule with a given id, marked as a given semester.
        Semester should be taken from parent scenario. 
        
        Returns the loaded schedule."""
        self.schedules[semester] = Schedule.read_DB(sid)
        return self.schedules[semester]

    # --------------------------------------------------------
    # reset_local
    # --------------------------------------------------------
    @staticmethod
    def reset_local():
        """ Reset the local model data """
        Block.reset()
        Course.reset()
        Lab.reset()
        Section.reset()
        Stream.reset()
        Teacher.reset()
        LabUnavailableTime.reset()
        Conflict.reset()

    @staticmethod
    @db_session
    def read_DB():
        """ Populates global Course, Lab, Teacher, & Stream lists from database """
        ScheduleWrapper.reset_local()

        course : db.Course
        for course in select(c for c in db.Course): Schedule._create_course(course.id)
        
        # create all labs
        lab : db.Lab
        for lab in select(l for l in db.Lab): Schedule._create_lab(lab.id)

        # create all teachers
        teacher : db.Teacher
        for teacher in select(t for t in db.Teacher): Schedule._create_teacher(teacher.id)

        stream : db.Stream
        for stream in select(s for s in db.Stream): Schedule._create_stream(stream.id)
    
    @staticmethod
    @db_session
    def write_DB():
        """ Saves global-level (Course, Lab, Teacher, Stream) changes to the database """
        # update all courses
        for c in Course.list(): c.save()
        
        # update all teachers
        for t in Teacher.list(): t.save()
        
        # update all streams
        for st in Stream.list(): st.save()
        
        # update all labs
        for l in Lab.list(): l.save()


@db_session
def scenarios(ignore_schedules : bool = False) -> tuple[Scenario]:
    """ Gets all scenarios from the database.
    # Important Note:
         Schedules contained within these scenarios have **not** been populated. Schedule.read_DB() or ScheduleWrapper.load_schedule() should be called to populate.
    """
    scens = set()
    scen : db.Scenario
    for scen in select(s for s in db.Scenario):
        sc = Scenario(scen.id, scen.name, scen.semester, scen.status, scen.description)
        scens.add(sc)
        if not ignore_schedules:
            scens.update(refresh_scenario_schedules(sc))
    
    return tuple(scens)

@db_session
def refresh_scenario_schedules(scen: Scenario):
    schedules = set()
    scenario = db.Scenario.get(id=scen.id)
    sched: db.Schedule
    for sched in select(sd for sd in db.Schedule if sd.scenario_id == scenario):
        schedule = Schedule(sched.id, sched.official, sched.scenario_id, sched.description)
        schedules.add(schedule)
    return schedules