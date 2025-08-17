"""
Grafana dashboard projection object
"""
from horey.common_utils.common_utils import CommonUtils
from horey.grafana_api.grafana_object import GrafanaObject
from horey.grafana_api.panel import Panel


class Dashboard(GrafanaObject):
    """
    Grafana dashboard projection object class
    """

    def __init__(self, dict_src):
        super().__init__()
        self.metadata = None
        self.spec = None
        self.status = None
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
            "metadata": self.metadata,
            "spec": self.spec,
            "panels": [panel.generate_create_request() for panel in panels]
        }

        if not ret["metadata"].get("name"):
            ret["metadata"]["name"] = "metadata.generateName"

        if not ret["metadata"].get("uid"):
            try:
                del ret["metadata"]["uid"]
            except KeyError:
                pass

        return ret

    def init_panels(self, key, list_src):
        """
        From dict

        :param key:
        :param dict_src:
        :return:
        """

        for dict_src in list_src:
            self.add_panel(Panel(dict_src))

    def add_panel(self, panel: Panel):
        """
        Add another panel to dashboard.

        :param panel:
        :return:
        """

        try:
            if panel.id is not None:
                raise NotImplementedError("Check panel id")
            panel.id = self.panels[-1].id+1
        except IndexError:
            panel.id = 1

        self.panels.append(panel)

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
