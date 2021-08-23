"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region
from enum import Enum


class ECSService(AwsObject):
    """
    AWS ECSService class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.propagate_tags = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "serviceArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "serviceName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "clusterArn": self.init_default_attr,
            "loadBalancers": self.init_default_attr,
            "serviceRegistries": self.init_default_attr,
            "desiredCount": self.init_default_attr,
            "runningCount": self.init_default_attr,
            "pendingCount": self.init_default_attr,
            "capacityProviderStrategy": self.init_default_attr,
            "taskDefinition": self.init_default_attr,
            "deploymentConfiguration": self.init_default_attr,
            "deployments": self.init_default_attr,
            "roleArn": self.init_default_attr,
            "events": self.init_default_attr,
            "createdAt": self.init_default_attr,
            "placementConstraints": self.init_default_attr,
            "placementStrategy": self.init_default_attr,
            "healthCheckGracePeriodSeconds": self.init_default_attr,
            "schedulingStrategy": self.init_default_attr,
            "createdBy": self.init_default_attr,
            "enableECSManagedTags": self.init_default_attr,
            "propagateTags": self.init_default_attr,
            "enableExecuteCommand": self.init_default_attr,
            "status": self.init_default_attr,
            "launchType": self.init_default_attr,
            "tags": self.init_default_attr,
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
            "serviceArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "serviceName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "clusterArn": self.init_default_attr,
            "loadBalancers": self.init_default_attr,
            "serviceRegistries": self.init_default_attr,
            "desiredCount": self.init_default_attr,
            "runningCount": self.init_default_attr,
            "pendingCount": self.init_default_attr,
            "capacityProviderStrategy": self.init_default_attr,
            "taskDefinition": self.init_default_attr,
            "deploymentConfiguration": self.init_default_attr,
            "deployments": self.init_default_attr,
            "roleArn": self.init_default_attr,
            "events": self.init_default_attr,
            "createdAt": self.init_default_attr,
            "placementConstraints": self.init_default_attr,
            "placementStrategy": self.init_default_attr,
            "healthCheckGracePeriodSeconds": self.init_default_attr,
            "schedulingStrategy": self.init_default_attr,
            "createdBy": self.init_default_attr,
            "enableECSManagedTags": self.init_default_attr,
            "propagateTags": self.init_default_attr,
            "enableExecuteCommand": self.init_default_attr,
            "status": self.init_default_attr,
            "launchType": self.init_default_attr,
            "tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["serviceName"] = self.name
        request["cluster"] = self.cluster_arn
        request["taskDefinition"] = self.task_definition
        request["loadBalancers"] = self.load_balancers
        request["desiredCount"] = self.desired_count

        request["launchType"] = self.launch_type

        request["role"] = self.role_arn
        request["deploymentConfiguration"] = self.deployment_configuration
        request["placementStrategy"] = self.placement_strategy
        request["healthCheckGracePeriodSeconds"] = self.health_check_grace_period_seconds
        request["schedulingStrategy"] = self.scheduling_strategy
        request["enableECSManagedTags"] = self.enable_ecs_managed_tags
        if self.propagate_tags is not None:
            request["propagateTags"] = self.propagate_tags
        request["enableExecuteCommand"] = self.enable_execute_command

        request["tags"] = self.tags
        return request

    def generate_update_request(self):
        request = dict()
        request["service"] = self.name
        request["cluster"] = self.cluster_arn
        request["taskDefinition"] = self.task_definition
        request["desiredCount"] = self.desired_count
        request["deploymentConfiguration"] = self.deployment_configuration
        request["placementStrategy"] = self.placement_strategy
        request["healthCheckGracePeriodSeconds"] = self.health_check_grace_period_seconds
        request["enableExecuteCommand"] = self.enable_execute_command

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

    def get_status(self):
        raise NotImplementedError()
        if self.status is None:
            return self.Status.ACTIVE
        elif self.status == "Delete in progress":
            return self.Status.DELETING
        else:
            raise NotImplementedError(self.status)

    class Status(Enum):
        ACTIVE = 0
        DELETING = 1
