"""
Grafana dashboard projection object
"""
from horey.grafana_api.grafana_object import GrafanaObject


class Dashboard(GrafanaObject):
    """
    Grafana dashboard projection object class
    """

    def __init__(self, dict_src):
        self.rows = None
        self.panels = []
        self.id = None
        self.uid = None
        self.title = None
        self.tags = []

        super().__init__()
        options = {
            "id": self.init_default,
            "uid": self.init_default,
            "title": self.init_default,
            "uri": self.init_default,
            "url": self.init_default,
            "slug": self.init_default,
            "type": self.init_default,
            "tags": self.init_default,
            "isStarred": self.init_default,
            "folderId": self.init_default,
            "folderUid": self.init_default,
            "folderTitle": self.init_default,
            "folderUrl": self.init_default,
            "sortMeta": self.init_default,
            "description": self.init_default,
            "gnetId": self.init_default,
        }

        self.init_values(dict_src, options)

    def update_full_info(self, dict_src):
        """
        Update full information from raw server response
        @param dict_src:
        @return:
        """
        options = {
            "meta": self.init_default,
            "annotations": self.init_default,
            "editable": self.init_default,
            "fiscalYearStartMonth": self.init_default,
            "graphTooltip": self.init_default,
            "hideControls": self.init_default,
            "id": self.init_default,
            "links": self.init_default,
            "liveNow": self.init_default,
            "panels": self.init_default,
            "schemaVersion": self.init_default,
            "style": self.init_default,
            "tags": self.init_default,
            "templating": self.init_default,
            "time": self.init_default,
            "timepicker": self.init_default,
            "timezone": self.init_default,
            "title": self.init_default,
            "uid": self.init_default,
            "version": self.init_default,
            "weekStart": self.init_default,
            "rows": self.init_default,
            "refresh": self.init_default,
            "description": self.init_default,
            "gnetId": self.init_default,
        }
        self.init_values(dict_src, options)

    def generate_create_request(self):
        """
        Generate create dashboard raw request
        @return:
        """

        self.generate_panels_positions()

        ret = {
            "dashboard": {
                "id": self.id,
                "title": self.title,
                "tags": self.tags,
                "timezone": "browser",
                "panels": [panel.generate_create_request() for panel in self.panels],
                "schemaVersion": 6,
                "version": 0,
            },
            "overwrite": True,
        }

        return ret

    def add_panel(self, panel):
        """
        Add another panel to dashbaord.

        :param panel:
        :return:
        """

        try:
            panel.id = self.panels[-1].id+1
        except IndexError:
            panel.id = 1

        self.panels.append(panel)

    def generate_panels_positions(self):
        """
        Generate x,y according to panels' sizes.

        :return:
        """

        y = 0
        x = 0
        last_panel_height = 0
        last_panel_width = 0

        for panel in self.panels:
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
