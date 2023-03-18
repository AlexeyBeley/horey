"""
Parent module for all grafana objects
"""

from horey.common_utils.common_utils import CommonUtils


class GrafanaObject:
    """
    Parent class for all grafana objects
    """

    def __init__(self):
        self.dict_src = {}

    def init_values(self, dict_src, options):
        """
        Init object values from raw server response
        @param dict_src:
        @param options:
        @return:
        """
        bugs = []
        for key, value in dict_src.items():
            self.dict_src[key] = value
            if key not in options:
                bugs.append(key)
                continue
            options[key](key, value)
        if bugs:
            str_error = "\n".join([f'"{key}": self.init_default,' for key in bugs])
            raise RuntimeError(str_error)

    def generate_create_request(self):
        """
        Each object will generate its request
        @return:
        """
        raise NotImplementedError()

    def init_default(self, key, value):
        """
        Default key/value initiation
        @param key:
        @param value:
        @return:
        """
        key = CommonUtils.camel_case_to_snake_case(key)
        setattr(self, key, value)
