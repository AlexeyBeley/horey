"""
Github actions base object
"""

import yaml
from horey.common_utils.common_utils import CommonUtils

class BaseObject:
    """
    Main class
    """

    def __init__(self):
        self.dict_src = None

    def _init_from_file(self, file_path):
        """
        Init from yaml

        """

        with open(file_path, "r", encoding="utf-8") as file:
            self.dict_src = yaml.safe_load(file)

        return True

    def init_from_api(self, dict_src:dict):
        """
        Init self parts
        """

        self.dict_src = dict_src
        CommonUtils.init_from_api_dict(self, dict_src)

        return True
