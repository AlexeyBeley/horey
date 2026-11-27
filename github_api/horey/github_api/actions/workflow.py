"""
Github Workflow
"""

import copy
from pathlib import Path
from horey.github_api.actions.job import Job
from horey.github_api.actions.base_object import BaseObject
from horey.common_utils.common_utils import CommonUtils

class Workflow(BaseObject):
    """
    Github Workflow
    """

    def __init__(self):
        super().__init__()
        self.name = None
        self.jobs = []
        self.on = None
        self.permissions = None
        self.concurrency = None
        self.id = None
        self.node_id = None
        self.path = None
        self.state = None
        self.created_at = None
        self.updated_at = None
        self.url = None
        self.html_url = None
        self.badge_url = None

    def init_from_file(self, file_path:Path):
        """
        Init self parts
        """

        self._init_from_file(file_path)

        dict_src = self.init_on(self.dict_src)

        # need to implemet "custom_setters" in init_from_api_dict instead of only custom_types
        # to handled "runs-on"
        custom_types = {"jobs": self.init_jobs}
        CommonUtils.init_from_api_dict(self, dict_src, custom_types=custom_types)

        return True

    def init_on(self, dict_src_base):
        """
        Init On
        """

        known_keys = ["push", "pull_request", "workflow_dispatch", "workflow_run", "workflow_call"]
        if True in dict_src_base:
            for key in dict_src_base[True]:
                if key not in known_keys:
                    raise NotImplementedError(f"Horey has not yet validated 'on' instruction with value {key}")
        dict_src = copy.deepcopy(dict_src_base)
        dict_src.pop(True)
        return dict_src

    def init_jobs(self, jobs_dict):
        """
        Init jobs
        """

        ret = []
        for job_name, job_dict in jobs_dict.items():
            job = Job(job_name)
            job.init_from_dict(job_dict)
            ret.append(job)
        return ret
