from horey.grafana_api.grafana_object import GrafanaObject


class Dashboard(GrafanaObject):
    def __init__(self, dict_src):
        self.rows = None
        self.panels = None
        self.id = None
        self.title = None
        self.tags = []

        super().__init__()
        options = {"id": self.init_default,
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
                   "sortMeta": self.init_default, }

        self.init_values(dict_src, options)

    def update_full_info(self, dict_src):
        options = {"meta": self.init_default,
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
                   }
        self.init_values(dict_src, options)

    def generate_create_request(self):
        return {"dashboard": {
            "id": self.id,
            "title": self.title,
            "tags": self.tags,
            "timezone": "browser",
            "rows": [
                {
                }
            ],
            "schemaVersion": 6,
            "version": 0
        },
            "overwrite": False
        }
