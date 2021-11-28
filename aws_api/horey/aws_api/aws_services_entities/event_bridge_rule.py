"""
Event bridge rule representation
"""

import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class EventBridgeRule(AwsObject):
    """
    AWS EventBridgeRule class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.targets = None
        self.arn = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Arn": self.init_default_attr,
            "Name": self.init_default_attr,
            "EventPattern": self.init_default_attr,
            "State": self.init_default_attr,
            "Description": self.init_default_attr,
            "ScheduleExpression": self.init_default_attr,
            "RoleArn": self.init_default_attr,
            "ManagedBy": self.init_default_attr,
            "EventBusName": self.init_default_attr,
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
            "RuleArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "Name": self.init_default_attr,
            "Arn": self.init_default_attr,
            "State": self.init_default_attr,
            "Description": self.init_default_attr,
            "ScheduleExpression": self.init_default_attr,
            "EventBusName": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["Name"] = self.name
        request["Tags"] = self.tags
        request["ScheduleExpression"] = self.schedule_expression
        request["State"] = self.state
        request["Description"] = self.description
        request["EventBusName"] = self.event_bus_name

        return request

    def generate_put_targets_request(self):
        if not self.targets:
            return

        request = dict()
        request["Rule"] = self.name
        request["EventBusName"] = self.event_bus_name
        request["Targets"] = [target.generate_put_request() for target in self.targets]
        return request

    @property
    def region(self):
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
