"""
Common parent to all work.
"""
import datetime
from enum import Enum
from horey.common_utils.common_utils import CommonUtils
from horey.common_utils.text_block import TextBlock


# pylint: disable= too-many-instance-attributes
class WorkObject:
    """
    Common data to all Work objects.
    """

    def __init__(self):
        self.id = None
        self.hapi_uid = None
        self.status = None
        self.created_date = None
        self._closed_date = None
        self.state_change_date = None
        self.created_by = None
        self.assigned_to = None
        self.title = None
        self.sprint_name = None
        self.child_ids = []
        self.child_hapi_uids = []
        self.parent_ids = []
        self.children = []
        self.azure_devops_object = None
        self.estimated_time = None
        self.comment = None

        self.dod = None
        self.priority = None
        self.description = None
        self.type = self.__class__.__name__

    @property
    def closed_date(self):
        """
        Close/Resolve/status change
        :return:
        """
        if self._closed_date is None:
            self._closed_date = self.state_change_date
        return self._closed_date

    @closed_date.setter
    def closed_date(self, value):
        self._closed_date = value

    def init_from_dict(self, dict_src):
        """
        Init attributes from standard dict.

        :param dict_src:
        :return:
        """
        properties = ["id", "hapi_uid", "status", "created_date", "closed_date", "created_by", "assigned_to",
                      "title", "sprint_name", "child_ids", "child_hapi_uids", "parent_ids",
                      "estimated_time", "comment", "dod", "priority", "description", "type"]

        for key in dict_src:
            if key not in properties:
                raise ValueError(key)
        custom_types = {"status": lambda x:  WorkObject.Status.__members__[x]}
        CommonUtils.init_from_dict(self, dict_src, custom_types=custom_types)

        if self.closed_date is not None and self.closed_date.tzinfo is not None:
            if self.closed_date.tzinfo != datetime.timezone.utc:
                raise ValueError("datetime.timezone.utc is only supported for now")
            self.closed_date = self.closed_date.replace(tzinfo=None)

        if self.created_date is not None and self.created_date.tzinfo is not None:
            if self.created_date.tzinfo != datetime.timezone.utc:
                raise ValueError("datetime.timezone.utc is only supported for now")
            self.created_date = self.created_date.replace(tzinfo=None)

    @staticmethod
    def wit_type_to_azure_devops_state(enum_value):
        """
        Convert Enum to a valid request string.

        :return:
        """

        if enum_value == WorkObject.Status.NEW:
            return "New"
        if enum_value == WorkObject.Status.ACTIVE:
            return "Active"
        if enum_value == WorkObject.Status.CLOSED:
            return "Closed"
        if enum_value == WorkObject.Status.BLOCKED:
            return "On Hold"

        raise ValueError(f"Wrong input for state: {enum_value}")

    class Status(Enum):
        """
        Task Vanilla status.

        """

        NEW = "NEW"
        ACTIVE = "ACTIVE"
        BLOCKED = "BLOCKED"
        CLOSED = "CLOSED"

    def generate_report_token(self):
        """
        Generate token to the daily report.

        :return:
        """
        return f"{self.__class__.__name__} {self.id} #{self.title}"

    def add(self, child):
        """
        Add a child.

        :param child:
        :return:
        """

        self.children.append(child)

    def convert_to_dict(self):
        """
        Convert the object to dict.

        :return:
        """

        default = WorkObject()
        ret = {key: getattr(self, key) for key in self.__dict__ if getattr(self, key) != getattr(default, key)}
        ret["type"] = self.__class__.__name__

        return CommonUtils.convert_to_dict(ret)

    def generate_summary(self):
        """
        Generate summary for the item

        :return:
        """

        htb_ret = TextBlock(f"{self.type}:")
        htb_ret.lines = [f"-- {self.title} --"]
        if self.description:
            htb_ret.lines.append("Description> " + self.description)

        if self.estimated_time:
            htb_ret.lines.append(f"Estimated> {self.estimated_time} hours")

        if self.dod:
            dod = ["DOD>"] + [f"{number}) " + value for number, value in enumerate(self.dod.values())]
            htb_ret.lines += dod

        if self.comment:
            comment = "Comment> " + self.comment
            htb_ret.lines.append(comment)

        return htb_ret
