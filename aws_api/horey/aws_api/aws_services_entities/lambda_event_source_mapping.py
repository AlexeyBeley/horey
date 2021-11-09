"""
AWS lambda_event_source_mapping representation
"""
import sys
import os
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region

class LambdaEventSourceMapping(AwsObject):
    """
    lambda_event_source_mapping representation class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.vpc_config = None
        self._region = None

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
        pdb.set_trace()
        init_options = {
            "QueueUrl": self.init_default_attr,
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
        pdb.set_trace()
        request = dict()
        request["QueueName"] = self.name
        request["tags"] = self.tags

        attributes = {}
        if self.delay_seconds is not None:
            attributes["DelaySeconds"] = self.delay_seconds
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
