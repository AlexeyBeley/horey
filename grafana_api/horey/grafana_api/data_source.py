"""
Grafana dashboard projection object
"""

from horey.grafana_api.grafana_object import GrafanaObject


class DataSource(GrafanaObject):
    """
    Grafana dashboard projection object class
    """
    def __init__(self, dict_src):
        super().__init__()
        self.id = None
        options = {"id": self.init_default,
                   "uid": self.init_default,
                   "orgId": self.init_default,
                   "name": self.init_default,
                   "type": self.init_default,
                   "typeName": self.init_default,
                   "typeLogoUrl": self.init_default,
                   "access": self.init_default,
                   "url": self.init_default,
                   "password": self.init_default,
                   "user": self.init_default,
                   "database": self.init_default,
                   "basicAuth": self.init_default,
                   "isDefault": self.init_default,
                   "jsonData": self.init_default,
                   "readOnly": self.init_default,
                   }

        self.init_values(dict_src, options)

    def generate_create_request(self):
        """
        Generate create datasource raw request
        @return:
        """
        if not self.dict_src:
            raise RuntimeError()
        return self.dict_src
