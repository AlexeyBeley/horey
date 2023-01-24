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
        function_identification - parameter being used in create_event_source_mapping.
        @param dict_src:
        @param from_cache:
        """
        self.vpc_config = None
        self._region = None
        self.function_identification = None
        self.state = None
        self.event_source_arn = None
        self.enabled = None
        self.arn = None

        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

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
        }

        self.init_attrs(dict_src, init_options)

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

        request = {"EventSourceArn": self.event_source_arn, "FunctionName": self.function_identification,
                   "Enabled": self.enabled}

        return request

    @property
    def region(self):
        """
        Self region.

        :return:
        """

        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        """
        Region setter.

        :param value:
        :return:
        """

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
