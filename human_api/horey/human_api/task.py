"""
Task
"""

from horey.human_api.work_object import WorkObject


class Task(WorkObject):
    """
    Work item -task, user story, feature, epic etc.
    """

    def init_from_azure_devops_work_item(self, work_item):
        """
        Init self from azure_devops work item
        :param work_item:
        :return:
        """
        self.init_from_azure_devops_work_item_base(work_item)
