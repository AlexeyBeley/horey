"""
Module handling jenkins job.
All steps - from being triggered to the final result.
"""
import uuid


class JenkinsJob:
    """
    Class handling Jenkins job. Has all attributes to manage it's current step.
    """

    def __init__(self, name, parameters, uid_parameter_name=None):
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

    def get_request_parameters(self):
        """
        Generate parameters as needed for correct job triggering.
        :return:
        """
        parameters = self.parameters
        if self.uid_parameter_name is not None:
            parameters[self.uid_parameter_name] = self.uid
        return parameters
