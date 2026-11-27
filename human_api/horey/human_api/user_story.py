"""
User Story
"""


from horey.human_api.work_object import WorkObject


class UserStory(WorkObject):
    """
    Feature
    """

    def init_from_azure_devops_work_item(self, work_item):
        """
        Init self from azure_devops work item
        :param work_item:
        :return:
        """
        self.init_from_azure_devops_work_item_base(work_item)
