"""
Basic object.

"""

from horey.common_utils.common_utils import CommonUtils


class OpensearchObject:
    """
    Main class
    """
    def __init__(self, dict_src):
        self.dict_src = None
        CommonUtils.init_from_api_dict(self, dict_src)
