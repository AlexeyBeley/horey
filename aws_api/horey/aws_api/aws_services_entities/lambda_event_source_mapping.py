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

        breakpoint()
        if self._arn is None:
            self._arn = self.uuid

        return self._arn
