class Course:
    _max_id = 0
    
    def __init__(self, **kwargs):
        self.name = "C"  # temp assignment to avoid crashes in Block __str__
        # keep **kwargs and below code, allows YAML to work correctly (kwargs should be last param)
        for k, v in kwargs.items():
            try:
                if hasattr(self, f"__{k}"): setattr(self, f"__{k}", v)
                elif hasattr(self, f"_{k}"): setattr(self, f"_{k}", v)
                elif hasattr(self, f"{k}"): setattr(self, f"{k}", v)
                #if k == "id": Course._max_id -= 1
            except AttributeError: continue # hit get-only property