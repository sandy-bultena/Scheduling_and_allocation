from ..Schedule.Schedule import Schedule
from ..Schedule.ScheduleEnums import ResourceType

# TODO: This code may be unnecessary, but it is certainly no longer working with the code
#       that has been modified lately

class AllResources:
    def __init__(self, schedule: Schedule):
        # Get teacher info.
        teacher_array = schedule._teachers
        teacher_ordered = sorted(teacher_array, key=lambda t: t.lastname)
        teacher_names = []
        for teach in teacher_ordered:
            name = f"{teach.firstname[0:1].upper()} {teach.lastname}"
            teacher_names.append(name)

        # get_by_id lab info
        lab_array = schedule.labs
        lab_ordered = sorted(lab_array, key=lambda l: l.number)
        lab_names = []
        for lab in lab_ordered:
            lab_names.append(lab.number)

        # get_by_id stream info
        stream_array = schedule._streams
        stream_ordered = sorted(stream_array, key=lambda s: s.number)
        stream_names = []
        for stream in stream_ordered:
            stream_names.append(stream.number)

        self.teachers = ScheduablesByType(ResourceType.Teacher, 'Teacher View', teacher_names,
                                          teacher_ordered)
        self.labs = ScheduablesByType(ResourceType.Lab, 'Lab View', lab_names, lab_ordered)
        self.streams = ScheduablesByType(ResourceType.Stream, 'Stream View', stream_names,
                                         stream_ordered)

    def by_type(self, type: ResourceType):
        # The Perl version of this used strings for the resource_type parameter. Since we have an enum of
        # ViewTypes, we're using that instead.
        if type == ResourceType.Teacher:
            return self.teachers
        elif type == ResourceType.Lab:
            return self.labs
        elif type == ResourceType.Stream:
            return self.streams

    def valid_types(self):
        return ResourceType.Teacher, ResourceType.Lab, ResourceType.Stream

    def valid_view_type(self, type: ResourceType):
        # NOTE: This function doesn't seem to be used at all in the Perl code.
        # Honestly, we may not even need it.
        if type == ResourceType.Teacher:
            return 'teacher'
        if type == ResourceType.Stream:
            return 'stream'
        if type == ResourceType.Lab:
            return 'lab'
        raise ValueError(f"Invalid view type <{type}>\n")
