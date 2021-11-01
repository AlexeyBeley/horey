"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ECSContainerInstance(AwsObject):
    """
    AWS VPC class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "containerInstanceArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "ec2InstanceId": self.init_default_attr,
            "capacityProviderName": self.init_default_attr,
            "version": self.init_default_attr,
            "versionInfo": self.init_default_attr,
            "remainingResources": self.init_default_attr,
            "registeredResources": self.init_default_attr,
            "status": self.init_default_attr,
            "agentConnected": self.init_default_attr,
            "runningTasksCount": self.init_default_attr,
            "pendingTasksCount": self.init_default_attr,
            "attributes": self.init_default_attr,
            "registeredAt": self.init_default_attr,
            "attachments": self.init_default_attr,
            "tags": self.init_default_attr,
            "agentUpdateStatus": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        init_options = {
        }

        self.init_attrs(dict_src, init_options)

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

    def generate_dispose_request(self, cluster):
        request = dict()
        request["cluster"] = cluster.name
        request["containerInstance"] = self.arn
        request["force"] = True
        return request
