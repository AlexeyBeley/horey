"""
Github Workflow
"""

from horey.github_api.actions.base_object import BaseObject

class WorkflowRun(BaseObject):
    """
    Github Workflow
    """

    # pylint: disable = too-many-instance-attributes
    def __init__(self):
        super().__init__()
        self.id = None
        self.name = None
        self.node_id = None
        self.head_branch = None
        self.head_sha = None
        self.path = ""
        self.display_title = None
        self.run_number = None
        self.event = None
        self.status = None
        self.conclusion = None
        self.workflow_id = None
        self.check_suite_id = None
        self.check_suite_node_id = None
        self.url = None
        self.html_url = None
        self.pull_requests = None
        self.created_at = None
        self.updated_at = None
        self.actor = None
        self.run_attempt = None
        self.referenced_workflows = None
        self.run_started_at = None
        self.triggering_actor = None
        self.jobs_url = None
        self.logs_url = None
        self.check_suite_url = None
        self.artifacts_url = None
        self.cancel_url = None
        self.rerun_url = None
        self.previous_attempt_url = None
        self.workflow_url = None
        self.head_commit = None
        self.repository = None
        self.head_repository = None

    def print(self):
        """
        Print
        """

        for key, value in self.__dict__.items():
            if key == "dict_src":
                continue
            print(f"{key}: {value}")
