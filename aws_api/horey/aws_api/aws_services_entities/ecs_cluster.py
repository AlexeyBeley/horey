"""
AWS Object representation
"""

from enum import Enum
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ECSCluster(AwsObject):
    """
    ECSCluster Object
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.capacity_providers = None
        self.default_capacity_provider_strategy = None
        self.registered_container_instances_count = None
        self.settings = None
        self.configuration = None
        self.status = None
        self.registered_container_instances_count = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """
        init_options = {
            "clusterArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "clusterName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "status": self.init_default_attr,
            "registeredContainerInstancesCount": self.init_default_attr,
            "runningTasksCount": self.init_default_attr,
            "pendingTasksCount": self.init_default_attr,
            "activeServicesCount": self.init_default_attr,
            "statistics": self.init_default_attr,
            "tags": self.init_default_attr,
            "settings": self.init_default_attr,
            "capacityProviders": self.init_default_attr,
            "defaultCapacityProviderStrategy": self.init_default_attr,
            "attachments": self.init_default_attr,
            "attachmentsStatus": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        request = {"clusterName": self.name, "tags": self.tags, "settings": self.settings,
                   "configuration": self.configuration}
        self.extend_request_with_optional_parameters(request, ["capacityProviders", "defaultCapacityProviderStrategy"])

        return request

    def generate_capacity_providers_request(self, cluster_desired):
        """
        Standard.

        :return:
        """

        if not cluster_desired.default_capacity_provider_strategy and not cluster_desired.capacity_providers:
            return None

        if self.capacity_providers != cluster_desired.capacity_providers or \
                self.default_capacity_provider_strategy != cluster_desired.default_capacity_provider_strategy:
            return {
                "cluster": self.name,
                "capacityProviders": cluster_desired.capacity_providers,
                "defaultCapacityProviderStrategy": cluster_desired.default_capacity_provider_strategy,
            }

        return None

    @property
    def region(self):
        if self._region is not None:
            return self._region

        if self.arn is None:
            raise NotImplementedError()
        self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """

        request = {"cluster": self.name}
        return request

    def get_status(self):
        """
        Standard function of the 'waiter' functional.

        :return:
        """

        return self.Status[self.status]

    class Status(Enum):
        """
        Status for get_status
        """
        ACTIVE = 0
        PROVISIONING = 1
        DEPROVISIONING = 2
        FAILED = 3
        INACTIVE = 4
