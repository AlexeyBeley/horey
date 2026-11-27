"""
AWS lambda_event_source_mapping representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class LambdaEventSourceMapping(AwsObject):
    """
    lambda_event_source_mapping representation class
    """

    def __init__(self, dict_src, from_cache=False):
        """
        @param dict_src:
        @param from_cache:
        """
        self.vpc_config = None
        self._region = None
        self.state = None
        self.event_source_arn = None
        self.function_arn = None
        self.enabled = None
        self.uuid = None

        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    @property
    def function_name(self):
        """
        Function name from arn

        :return:
        """

        lst_arn = self.function_arn.split(":")
        if lst_arn[5] != "function":
            raise ValueError(self.function_arn)

        return lst_arn[6]

    def update_from_raw_response(self, dict_src):
        """
        Response from server.

        :param dict_src:
        :return:
        """

        init_options = {
            "FunctionArn": self.init_default_attr,
            "UUID": self.init_default_attr,
            "StartingPosition": self.init_default_attr,
            "BatchSize": self.init_default_attr,
            "MaximumBatchingWindowInSeconds": self.init_default_attr,
            "ParallelizationFactor": self.init_default_attr,
            "EventSourceArn": self.init_default_attr,
            "LastModified": self.init_default_attr,
            "LastProcessingResult": self.init_default_attr,
            "State": self.init_default_attr,
            "StateTransitionReason": self.init_default_attr,
            "DestinationConfig": self.init_default_attr,
            "MaximumRecordAgeInSeconds": self.init_default_attr,
            "BisectBatchOnFunctionError": self.init_default_attr,
            "MaximumRetryAttempts": self.init_default_attr,
            "TumblingWindowInSeconds": self.init_default_attr,
            "FunctionResponseTypes": self.init_default_attr,
            "EventSourceMappingArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
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

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        return self.generate_request(["EventSourceArn", "FunctionName", "Enabled"], optional=["StartingPosition", "BatchSize"])

    @property
    def arn(self):
        """
        Self arn.

        :return:
        """

        if self._arn is None:
            if not self.account_id:
                raise RuntimeError("Can not generate arn, account_id was not set")
            self._arn = f"arn:aws:lambda:{self.region.region_mark}:{self.account_id}:event-source-mapping:{self.uuid}"

        return self._arn

    @arn.setter
    def arn(self, value):
        self._arn = value

    def generate_modify_tags_requests(self, desired_state):
        """
        Add tags, delete tags.

        :param desired_state:
        :return:
        """

        tag_keys, untag_keys = {}, []

        for key, value in self.tags.items():
            if key not in desired_state.tags:
                untag_keys.append(key)

        for key, value in desired_state.tags.items():
            if self.tags.get(key) != value:
                tag_keys[key] = value

        tag_resource_request = {"Resource": self.arn, "Tags": tag_keys} if tag_keys else None
        untag_resource_request = {"Resource": self.arn, "TagKeys": untag_keys} if untag_keys else None
        return tag_resource_request, untag_resource_request
