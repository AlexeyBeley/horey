from horey.azure_api.azure_service_entities.azure_object import AzureObject


class ResourceGroup(AzureObject):
    def __init__(self, dict_src, from_cache=False):
        self.statements = []

        super().__init__(dict_src, from_cache=from_cache)

        if from_cache:
            self.init_resource_group_from_cache(dict_src)
            return

        init_options = {
                        "id": self.init_default_attr,
                        }

        self.init_attrs(dict_src, init_options)

    def init_resource_group_from_cache(self):
        raise NotImplementedError()