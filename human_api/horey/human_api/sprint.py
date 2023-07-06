"""
Sprint obj

"""


class Sprint:
    """
    Single iteration

    """

    def __init__(self):
        self.id = None
        self.name = None
        self.start_date = None
        self.finish_date = None
        self.azure_devops_object = None

    def init_from_azure_devops_iteration(self, iteration):
        """
        Init self from azure_devops iteration

        :param iteration:
        :return:
        """
        self.azure_devops_object = iteration
        self.id = iteration.path
        self.name = iteration.name
        self.start_date = iteration.start_date
        self.finish_date = iteration.finish_date
