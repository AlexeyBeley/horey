"""
Grafana dashboard projection object
"""
import copy

from horey.common_utils.common_utils import CommonUtils
from horey.grafana_api.grafana_object import GrafanaObject
from horey.grafana_api.panel import Panel


class Dashboard(GrafanaObject):
    """
    Grafana dashboard projection object class
    """

    def __init__(self, dict_src):
        super().__init__()
        self.metadata = {}
        self.spec = {}
        self.status = {}
        self.api_version = None
        self.kind = None
        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Update from server response.

        :param dict_src:
        :return:
        """

        CommonUtils.init_from_api_dict(self, dict_src)

    def generate_create_request(self):
        """
        Generate create dashboard raw request
        @return:
        """

        panels = self.generate_panels_with_positions(self.spec["panels"])

        ret = {
            "metadata": copy.deepcopy(self.metadata),
            "spec": copy.deepcopy(self.spec),
            "panels": [panel.generate_create_request() for panel in panels]
        }

        slug = self.spec["title"].replace(" ", "-")
        if not ret["metadata"].get("name"):
            ret["metadata"]["name"] = slug

        if not ret["metadata"].get("uid"):
            ret["metadata"]["uid"] = slug
        return ret

    def generate_panels_with_positions(self, lst_panels_dicts):
        """
        Generate x,y according to panels' sizes.

        :return:
        """

        panels = [Panel(panel_dict) for panel_dict in lst_panels_dicts]
        if not panels:
            return panels
        y = 0
        x = 0
        last_panel_height = 0
        last_panel_width = 0

        for panel in panels:
            if panel.width == 24:
                x = 0
                y = y + last_panel_height
            else:
                x = x + last_panel_width
                if x == 24:
                    y = y + last_panel_height
                    x = 0

            panel.generate_position(x, y)
            last_panel_height = panel.height
            last_panel_width = panel.width
        return panels
