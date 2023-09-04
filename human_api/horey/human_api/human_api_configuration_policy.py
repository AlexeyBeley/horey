"""
Configs
"""
import datetime
import os

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

# pylint: disable= missing-function-docstring


class HumanAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class
    """
    def __init__(self):
        self._azure_devops_api_configuration_file_path = None
        self._reports_dir_path = None
        self._work_plan_file_path = None
        self._sprint_name = None
        self._ignore_workers = None
        self._backlog_sprint_name = None
        super().__init__()

    @property
    def azure_devops_api_configuration_file_path(self):
        if self._azure_devops_api_configuration_file_path is None:
            raise ValueError("azure_devops_api_configuration_file_path was not set")
        return self._azure_devops_api_configuration_file_path

    @azure_devops_api_configuration_file_path.setter
    def azure_devops_api_configuration_file_path(self, value):
        """
        http://127.0.0.1:8888
        @param value:
        @return:
        """

        if not isinstance(value, str):
            raise ValueError(
                f"azure_devops_api_configuration_file_path must be string received {value} of type: {type(value)}"
            )

        self._azure_devops_api_configuration_file_path = value

    @property
    def daily_hapi_file_path(self):
        return os.path.join(self.daily_dir_path, "daily.hapi")

    @property
    def protected_input_file_path(self):
        return os.path.join(self.daily_dir_path, "input.hapi")

    @property
    def daily_hr_output_file_path(self):
        return os.path.join(self.daily_dir_path, "hr_output.hapi")

    @property
    def output_file_path(self):
        return os.path.join(self.daily_dir_path, "ytb.hapi")

    @property
    def work_status_file_name(self):
        return "work_status.json"

    @property
    def work_status_file_path(self):
        return os.path.join(self.daily_dir_path, self.work_status_file_name)

    @property
    def big_brother_file_path(self):
        return os.path.join(self.daily_dir_path, "big_brother.hapi")

    @property
    def sprint_dir_path(self):
        ret = os.path.join(self.reports_dir_path, self.sprint_name.replace(" ", "_"))
        os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def daily_dir_path(self):
        ret = os.path.join(self.sprint_dir_path, str(datetime.date.today()))
        os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def sprint_retrospective_dir_path(self):
        ret = os.path.join(self.sprint_dir_path, "retrospective")
        os.makedirs(ret, exist_ok=True)
        return ret

    @property
    def sprint_start_status_file_path(self):
        ret = os.path.join(self.sprint_dir_path, "sprint_start_status.json")
        return ret

    @property
    def sprint_finish_status_file_path(self):
        ret = os.path.join(self.sprint_retrospective_dir_path, "sprint_finish_status.json")
        return ret

    @property
    def sprint_plan_retro(self):
        return os.path.join(self.sprint_dir_path, "sprint_plan_retro.py")

    @property
    def work_plan_output_file_path_template(self):
        return os.path.join(self.reports_dir_path, "{sprint_name}", "work_plan.json")

    @property
    def sprint_plan_file_path(self):
        return os.path.join(self.sprint_dir_path, "sprint_plan.py")

    @property
    def work_plan_output_file_path(self):
        return os.path.join(self.sprint_dir_path, "work_plan.json")


    @property
    def work_plan_summary_output_file_path_template(self):
        return os.path.join(self.reports_dir_path, "{sprint_name}", "hr_summary.txt")

    @property
    def reports_dir_path(self):
        if self._reports_dir_path is None:
            raise self.UndefinedValueError("reports_dir_path")
        return self._reports_dir_path

    @reports_dir_path.setter
    def reports_dir_path(self, value):
        self._reports_dir_path = value

    @property
    def sprint_name(self):
        if self._sprint_name is None:
            raise self.UndefinedValueError("sprint_name")
        return self._sprint_name

    @sprint_name.setter
    def sprint_name(self, value):
        self._sprint_name = value

    @property
    def ignore_workers(self):
        return self._ignore_workers

    @ignore_workers.setter
    def ignore_workers(self, value):
        self._ignore_workers = value

    @property
    def backlog_sprint_name(self):
        return self._backlog_sprint_name

    @backlog_sprint_name.setter
    def backlog_sprint_name(self, value):
        self._backlog_sprint_name = value
