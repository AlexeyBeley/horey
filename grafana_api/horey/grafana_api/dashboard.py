from horey.grafana_api.grafana_object import GrafanaObject


class Dashboard(GrafanaObject):
    def __init__(self, dict_src):
        self.rows = None
        self.id = None
        self.title = None
        self.tags = []
        super().__init__(dict_src)

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
