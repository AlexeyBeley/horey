"""
Grafana Folder class
"""
from horey.grafana_api.grafana_object import GrafanaObject


class Folder(GrafanaObject):
    """
    Main class

    """

    def __init__(self, dict_src):
        super().__init__()
        self.kind = None
        self.api_version = None
        self.metadata = None
        self.spec = None
        self.status = None

        options = {
            "apiVersion": self.init_default,
            "kind": self.init_default,
            "metadata": self.init_default,
            "spec": self.init_default,
            "status": self.init_default
        }
        self.init_values(dict_src, options)

    def generate_create_request(self):
        """
        Generates folder create request.

        :return:
        """

        raise NotImplementedError()
