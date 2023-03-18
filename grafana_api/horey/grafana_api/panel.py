"""
Grafana Panel projection object
"""
from horey.grafana_api.grafana_object import GrafanaObject
from horey.common_utils.common_utils import CommonUtils


class Panel(GrafanaObject):
    """
    Grafana Panel projection object class
    """

    def __init__(self, dict_src):
        """

        :param dict_src:
        """

        super().__init__()
        self.grid_pos = {}
        self._width = None
        self._height = None
        self.targets = []

        options = self.get_options()

        self.init_values(dict_src, options)

    def get_options(self):
        """
        Init options.

        :return:
        """

        return {
            "id": self.init_default,
            "gridPos": self.init_default,
            "type": self.init_default,
            "title": self.init_default,
            "datasource": self.init_default,
            "fieldConfig": self.init_default,
            "options": self.init_default,
            "targets": self.init_default,
            "panels": self.init_default,
            "collapsed": self.init_default,
        }

    def generate_create_request(self):
        """
        Generate create dashboard raw request
        @return:
        """
        req_ret = {}
        dict_options = {CommonUtils.camel_case_to_snake_case(option_name): option_name for option_name in self.get_options()}
        for attr, value in self.__dict__.items():
            if attr not in dict_options:
                continue
            req_ret[dict_options[attr]] = value

        return req_ret

    @property
    def width(self):
        """
        Panel width

        :return:
        """
        if self._width is None:
            width = self.grid_pos.get("w")
            if width is None:
                raise RuntimeError(f"'w' was not set in '{self.dict_src}'")
            self._width = width

        return self._width

    @property
    def height(self):
        """
        Panel height.

        :return:
        """

        if self._height is None:
            height = self.grid_pos.get("h")
            if height is None:
                raise RuntimeError(f"'h' was not set in '{self.dict_src}'")
            self._height = height

        return self._height

    def generate_position(self, left_x, top_y):
        """
        Set positions

        :param left_x:
        :param top_y:
        :return:
        """

        for attr in ["h", "w"]:
            if self.grid_pos.get(attr) is None:
                raise RuntimeError(f"'{attr}' was not set in '{self.dict_src}'")

        if left_x + self.width > 24:
            raise ValueError(f"left_x: '{left_x}' + self.width: '{self.width}' > 24 in '{self.dict_src}'")

        self.grid_pos["x"] = left_x
        self.grid_pos["y"] = top_y
