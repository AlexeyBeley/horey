"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ECSTaskDefinition(AwsObject):
    """
    AWS AutoScalingGroup class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "taskDefinitionArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
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
        init_options = {
            "taskDefinitionArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
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
        request = dict()
        request["name"] = self.name
        request["containerDefinitions"] = self.container_definitions
        request["tags"] = self.tags
        request["family"] = self.family
        request["taskRoleArn"] = self.task_role_arn
        request["executionRoleArn"] = self.execution_role_arn
        request["requiresCompatibilities"] = ["EC2"]

        request["cpu"] = self.cpu
        request["memory"] = self.memory

        return request

    @property
    def region(self):
        if self._region is not None:
            return self._region

        raise NotImplementedError()
        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
