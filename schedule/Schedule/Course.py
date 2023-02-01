class CourseMeta(type):
    _instances = {}

    def __iter__(self):
        return iter(getattr(self, '_instances', {}))

class Course(metaclass=CourseMeta):
    # ideally iterable is implemented with dict; if not, yaml write needs to be modified accordingly
    _max_id = 0
    
    def __init__(self, **kwargs):
        self.name = "C"  # temp assignment to avoid crashes in Block __str__