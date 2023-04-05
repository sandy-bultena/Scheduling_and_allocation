from ..Schedule.Schedule import Schedule
from ..Schedule.ScheduleEnums import ViewType


class AllScheduables:
    def __init__(self, schedule: Schedule):
        # Get teacher info.
        teacher_array = schedule.teachers()
        teacher_ordered = sorted(teacher_array, key=lambda t: t.lastname)
        teacher_names = []
        for teach in teacher_ordered:
            name = f"{teach.firstname[0:1].upper()} {teach.lastname}"
            teacher_names.append(name)

        # get lab info
        lab_array = schedule.labs()
        lab_ordered = sorted(lab_array, key=lambda l: l.number)
        lab_names = []
        for lab in lab_ordered:
            lab_names.append(lab.number)

        # get stream info
        stream_array = schedule.streams()
        stream_ordered = sorted(stream_array, key=lambda s: s.number)
        stream_names = []
        for stream in stream_ordered:
            stream_names.append(stream.number)

        self.teachers = ScheduablesByType('teacher', 'Teacher View', teacher_names, teacher_ordered)
        self.labs = ScheduablesByType('lab', 'Lab View', lab_names, lab_ordered)
        self.streams = ScheduablesByType('stream', 'Stream View', stream_names, stream_ordered)

    def by_type(self, type: ViewType):
        # The Perl version of this used strings for the type parameter. Since we have an enum of
        # ViewTypes, we're using that instead.
        if type == ViewType.Teacher:
            return self.teachers
        elif type == ViewType.Lab:
            return self.labs
        elif type == ViewType.Stream:
            return self.streams

    def valid_types(self):
        return 'teacher', 'stream', 'lab'

    def valid_view_type(self, type: ViewType):
        # NOTE: This function doesn't seem to be used at all in the Perl code.
        # Honestly, we may not even need it.
        if type == ViewType.Teacher:
            return 'teacher'
        if type == ViewType.Stream:
            return 'stream'
        if type == ViewType.Lab:
            return 'lab'
        raise ValueError(f"Invalid view type <{type}>\n")
