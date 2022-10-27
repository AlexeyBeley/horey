"""
Package requirement.

"""


class Requirement:
    """
    Main class.
    """
    def __init__(self, requirement_str):
        self.name = None
        self.min_version = None
        self.max_version = None
        self.include_min = None
        self.include_max = None

        if "==" in requirement_str:
            self.name, version = requirement_str.split("==")
            self.min_version = version
            self.max_version = version
            self.include_min = True
            self.include_max = True
        elif ">=" in requirement_str:
            self.name, version = requirement_str.split(">=")
            self.min_version = version
            self.include_min = True
        elif "<=" in requirement_str:
            self.name, version = requirement_str.split("<=")
            self.max_version = version
            self.include_max = True
        else:
            raise ValueError(requirement_str)
