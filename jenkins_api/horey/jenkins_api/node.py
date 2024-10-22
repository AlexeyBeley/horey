"""
Single Node representation

"""
from horey.common_utils.common_utils import CommonUtils


# pylint: disable= too-many-instance-attributes

class Node:
    """
    Jenkins executors node
    """

    def __init__(self, dict_src):
        self._class = None
        self.actions = None
        self.assigned_labels = None
        self.description = None
        self.display_name = None
        self.executors = None
        self.icon = None
        self.icon_class_name = None
        self.idle = None
        self.jnlp_agent = None
        self.launch_supported = None
        self.load_statistics = None
        self.manual_launch_allowed = None
        self.monitor_data = None
        self.num_executors = None
        self.offline = None
        self.offline_cause = None
        self.offline_cause_reason = None
        self.one_off_executors = None
        self.temporarily_offline = None
        self.absolute_remote_path = None

        if dict_src:
            self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Update from server response.

        :param dict_src:
        :return:
        """

        CommonUtils.init_from_api_dict(self, dict_src)
