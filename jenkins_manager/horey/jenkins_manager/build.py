"""
Single build representation

"""

import datetime

from horey.common_utils.common_utils import CommonUtils

#pylint: disable= too-many-instance-attributes

class Build:
    """
    Build - a job execution.

    """

    def __init__(self, dict_src):
        self._name = None
        self._class = None
        self.id = None
        self.actions = None
        self.artifacts = None
        self.building = None
        self.description = None
        self.display_name = None
        self.duration = None
        self.estimated_duration = None
        self.executor = None
        self.full_display_name = None
        self.keep_log = None
        self.number = None
        self.queue_id = None
        self.result = None
        self.timestamp = None
        self.url = None
        self.change_sets = None
        self.culprits = None
        self.next_build = None
        self.previous_build = None
        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Update from server response.

        :param dict_src:
        :return:
        """

        CommonUtils.init_from_api_dict(self, dict_src)

    @property
    def finished(self):
        """
        Returned the build execution finished running.

        :return:
        """
        return self.result is not None

    @property
    def name(self):
        """
        Build name
        :return:
        """
        if self._name is None:
            for attr in ["display_name", "number", "url"]:
                if getattr(self, attr) is None:
                    raise ValueError(f"{attr.capitalize()} was not set")

            hash_number = f"#{self.number}"
            if hash_number not in self.display_name:
                raise ValueError(f"'{hash_number}' was not found in {self.display_name=}")
            self._name = self.display_name[:self.display_name.find(hash_number)].strip()
            if f"/{self._name}/" not in self.url:
                raise ValueError(f"Can not find {self._name} in {self.url=}")

        return self._name

    @name.setter
    def name(self, value):
        """
        Setter

        :param value:
        :return:
        """

        self._name = value

    @property
    def start_time(self):
        """
        Build start time

        :return:
        """

        return datetime.datetime.fromtimestamp(self.timestamp/1000)

    @property
    def parameters_dict(self):
        """
        Convert parameters to key:value format. If not initiated return None

        :return: dict with params if initialized. None else.
        """

        if not self.actions:
            return None
        for action in self.actions:
            if action.get("_class") == "hudson.model.ParametersAction":
                return {param_dict["name"]: param_dict["value"] for param_dict in action["parameters"]}

        raise RuntimeError("Can not find action class: hudson.model.ParametersAction")

    def compare_parameters(self, required_parameters):
        """
        Compare parameters - only src to self checked. Self to src ignored. (Default values assumed)

        :param required_parameters:
        :return:
        """

        for key, value in required_parameters.items():
            if self.parameters_dict.get(key) != value:
                return False
        return True