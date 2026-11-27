"""
Event bridge rule representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EventBridgeRule(AwsObject):
    """
    AWS EventBridgeRule class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.targets = []
        self.schedule_expression = None
        self.state = None
        self.description = None
        self.event_bus_name = None

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
        """
        Standard

        :param dict_src:
        :return:
        """
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
        """
        Standard
        :return:
        """
        request = {"Name": self.name, "Tags": self.tags, "ScheduleExpression": self.schedule_expression,
                   "State": self.state, "Description": self.description, "EventBusName": self.event_bus_name}

        return request

    def generate_put_targets_request(self):
        """
        Standard
        :return:
        """
        if not self.targets:
            return None

        request = {"Rule": self.name,
                   "EventBusName": self.event_bus_name,
                   "Targets": [target.generate_put_request() for target in self.targets]}
        return request
