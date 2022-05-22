import pdb

from horey.grafana_api.grafana_object import GrafanaObject


class Folder(GrafanaObject):
    def __init__(self, dict_src):
        super().__init__(dict_src)

    def generate_create_request(self):
        raise NotImplementedError()
        return
