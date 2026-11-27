"""
Route table module
"""
from horey.azure_api.azure_service_entities.azure_object import AzureObject


class RouteTable(AzureObject):
    """
    Class to handle route tables

    """

    def __init__(self, dict_src, from_cache=False):
        self.name = None
        self.type = None
        self.location = None
        self.tags = None
        self.etag = None
        self.routes = None
        self.subnets = None
        self.disable_bgp_route_propagation = None
        self.provisioning_state = None
        self.resource_guid = None

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_from_cache(dict_src)
            return
        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        From API response.

        :param dict_src:
        :return:
        """

        init_options = {
            key: self.init_default_attr for key in
            ["id", "name", "type", "location", "tags",
             "etag", "routes", "subnets", "disable_bgp_route_propagation",
             "provisioning_state", "resource_guid"]
        }

        return self.init_attrs(dict_src, init_options)

    def init_from_cache(self, dict_src):
        """
        Init from cache.

        :param dict_src:
        :return:
        """
        raise NotImplementedError()

    def generate_create_request(self):
        """
        Generate request to create route table.

        :return:
        """

        ret = [
            self.resource_group_name,
            self.name,
            {
                "location": self.location,
                "routes": self.routes,
                "tags": self.tags,
            },
        ]

        return ret
