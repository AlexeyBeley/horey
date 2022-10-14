"""
Employee object
"""
from horey.bob_api.bob_object import BobObject


class Employee(BobObject):
    """
    Main class
    """
    def __init__(self, dict_src):
        self.full_name = None
        self.work = None
        self.display_name = None
        super().__init__(dict_src)
