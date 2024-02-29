"""
AWS Lambda representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ECSTaskDefinition(AwsObject):
    """
    AWS AutoScalingGroup class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.volumes = None
        self.network_mode = None
        self.requires_compatibilities = None
        self.memory = None
        self.cpu = None
        self.family = None
        self.container_definitions = None
        self.task_role_arn = None
        self.execution_role_arn = None
        self.arn = None
        self.runtime_platform = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "taskDefinitionArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "containerDefinitions": self.init_default_attr,
            "family": self.init_default_attr,
            "taskRoleArn": self.init_default_attr,
            "executionRoleArn": self.init_default_attr,
            "revision": self.init_default_attr,
            "volumes": self.init_default_attr,
            "requiresAttributes": self.init_default_attr,
            "placementConstraints": self.init_default_attr,
            "compatibilities": self.init_default_attr,
            "requiresCompatibilities": self.init_default_attr,
            "cpu": self.init_default_attr,
            "memory": self.init_default_attr,
            "registeredAt": self.init_default_attr,
            "registeredBy": self.init_default_attr,
            "status": self.init_default_attr,
            "networkMode": self.init_default_attr,
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
        """
        Object data from server dict reply.

        :param dict_src:
        :return:
        """

        init_options = {
            "taskDefinitionArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "containerDefinitions": self.init_default_attr,
            "family": self.init_default_attr,
            "taskRoleArn": self.init_default_attr,
            "executionRoleArn": self.init_default_attr,
            "revision": self.init_default_attr,
            "volumes": self.init_default_attr,
            "requiresAttributes": self.init_default_attr,
            "placementConstraints": self.init_default_attr,
            "compatibilities": self.init_default_attr,
            "requiresCompatibilities": self.init_default_attr,
            "cpu": self.init_default_attr,
            "memory": self.init_default_attr,
            "registeredAt": self.init_default_attr,
            "registeredBy": self.init_default_attr,
            "status": self.init_default_attr,
            "networkMode": self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Generate request from object.

        :return:
        """

        request = {"containerDefinitions": self.container_definitions, "tags": self.tags}

        self.extend_request_with_optional_parameters(request, ["networkMode",
                                                               "runtimePlatform",
                                                               "requiresCompatibilities",
                                                               "memory",
                                                               "cpu",
                                                               "volumes",
                                                               "executionRoleArn",
                                                               "taskRoleArn",
                                                               "family"])

        return request

    @property
    def region(self):
        """
        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

        :return:
        """

        if self._region is not None:
            return self._region

        raise NotImplementedError("todo: Region from ARN")

    @region.setter
    def region(self, value):
        """
        Set region

        :param value:
        :return:
        """

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
