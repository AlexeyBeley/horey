"""
Module handling jenkins job.
All steps - from being triggered to the final result.
"""
import uuid
from enum import Enum

class JenkinsJob:
    """
    Class handling Jenkins job. Has all attributes to manage it's current step.
    """

    def __init__(self, name, parameters, uid_parameter_name=None, cache_dict=None):
        """
        Uid_parameter_name - for jobs being able to be uniquely identified by it.
        For more info check Readme

        :param name:
        :param parameters:
        :param uid_parameter_name:
        """
        self.name = name
        self.parameters = parameters
        self.queue_item_id = None
        self.build_id = None
        self.build_status = None
        self.uid = str(uuid.uuid4())
        self.uid_parameter_name = uid_parameter_name

        if cache_dict is not None:
            self.init_from_cache_dict(cache_dict)

    def get_request_parameters(self):
        """
        Generate parameters as needed for correct job triggering.
        :return:
        """
        parameters = self.parameters
        if self.uid_parameter_name is not None:
            parameters[self.uid_parameter_name] = self.uid
        return parameters

    CACHE_VALUES = ["name", "parameters", "uid_parameter_name"]

    def convert_to_cache_dict(self):
        return {key: getattr(self, key) for key in self.CACHE_VALUES}

    def init_from_cache_dict(self, dict_src):
        for key in self.CACHE_VALUES:
            setattr(self, key, dict_src[key])

    @property
    def status(self):
        if self.build_status == "SUCCESS":
            return self.Status.SUCCESS
        raise NotImplementedError(self.build_status)

    class Status(Enum):
        SUCCESS = "SUCCESS"
