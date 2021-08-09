

class DebugUtils:
    @staticmethod
    def print_object(obj_src):
        for x in obj_src.__dict__.items():
            print(x)
