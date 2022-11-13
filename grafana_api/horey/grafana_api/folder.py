import pdb

from horey.grafana_api.grafana_object import GrafanaObject


class Folder(GrafanaObject):
    def __init__(self, dict_src):
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
            "sortMeta": self.init_default,
        }
        self.init_values(dict_src, options)

    def generate_create_request(self):
        raise NotImplementedError()
        return
