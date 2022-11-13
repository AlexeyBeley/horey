"""
All HiBob object share same base class.
"""
from horey.common_utils.common_utils import CommonUtils


class BobObject:
    """
    Main class
    """

    def __init__(self, dict_src):
        self.dict_src = dict_src
        self.init_attrs()

    def convert_to_dict(self):
        """
        Convert to dict.

        @return:
        """
        return self.dict_src

    def init_attrs(self):
        """
        Init default attributes

        @return:
        """
        for attr_name, attr_value in self.dict_src.items():
            setattr(self, CommonUtils.camel_case_to_snake_case(attr_name), attr_value)
