from ..Schedule.Schedule import Schedule


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
