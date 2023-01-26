class Course:
    def __init__(self, **kwargs):
        # keep **kwargs and below code, allows YAML to work correctly (kwargs should be last param)
        for k, v in kwargs.items():
            try:
                if hasattr(self, f"__{k}"): setattr(self, f"__{k}", v)
                elif hasattr(self, f"_{k}"): setattr(self, f"_{k}", v)
                elif hasattr(self, f"{k}"): setattr(self, f"{k}", v)
                #if k == "id": Course._max_id -= 1
            except AttributeError: continue # hit get-only property