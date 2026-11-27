"""
Worflow job

"""

from horey.common_utils.common_utils import CommonUtils

# pylint: disable = too-many-instance-attributes
class Job:
    """
    Main class
    """

    def __init__(self, name):
        self.name = name
        self.dict_src = None
        self.runs_on = None
        self.steps = []
        self.uses = None
        self.id = None
        self.env = None
        self.container = None
        self.outputs = None
        self.defaults = None
        self.timeout_minutes = None
        self.needs = None
        self._if = None
        self.secrets = None
        self._with = None
        self.permissions = None
        self.status = None
        self.conclusion = None
        self.started_at = None
        self.completed_at = None
        self.run_id = None
        self.run_url = None
        self.node_id = None
        self.head_sha = None
        self.url = None
        self.html_url = None
        self.check_run_url = None
        self.labels = None
        self.runner_id = None
        self.runner_name = None
        self.runner_group_id = None
        self.runner_group_name = None
        self.workflow_name = None
        self.head_branch = None
        self.run_attempt = None
        self.created_at = None

    def init_from_dict(self, dict_src):
        """
        Init
        """

        self.dict_src = dict_src
        def init_steps(steps):
            ret = []
            for step_dict in steps:
                step = self.Step()
                step.init_from_dict(step_dict)
                ret.append(step)
            return ret

        custom_types = {"steps": init_steps}
        CommonUtils.init_from_api_dict(self, dict_src, custom_types=custom_types)

        return True
    def print(self):
        """
        Print
        """

        for key, value in self.__dict__.items():
            if key == "dict_src":
                continue
            print(f"{key}: {value}")

    class Step:
        """
        Internal Step.
        """
        def __init__(self):
            self.id = None
            self.name = None
            self.env = None
            self.uses = None
            self._with = None
            self._if = None
            self.run = None
            self.shell = None
            self.shell = None
            self.status = None
            self.conclusion = None
            self.started_at = None
            self.completed_at = None
            self.number = None

        def init_from_dict(self, dict_src):
            """
            Init from dict
            """

            CommonUtils.init_from_api_dict(self, dict_src)

        def print(self):
            """
            Print
            """

            for key, value in self.__dict__.items():
                if key == "dict_src":
                    continue
                print(f"{key}: {value}")
