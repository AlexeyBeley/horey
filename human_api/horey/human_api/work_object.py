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
        self.completed_time = None
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
                      "estimated_time", "comment", "dod", "priority", "description", "type", "completed_time"]

        for key in dict_src:
            if key.startswith("_"):
                key = key[1:]
            if key not in properties:
                raise ValueError(f"Unknown property: {key}")
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

    def generate_python_self_param_name(self):
        """
        Generate the argument name for self representation in python.

        :return:
        """
        return f"{self.type.lower()}_{self.id}"

    def convert_to_python(self, indent=0, suppress=None):
        """
        Convert to python

        :return:
        """
        str_indent = " " * indent
        if self.id is None:
            raise ValueError("Not implemented for work objects without ID")

        param_name =  self.generate_python_self_param_name()
        lst_ret = [str_indent + f"{param_name} = {self.type}()"]
        for var_name in ["id", "sprint_name", "title"]:
            if suppress and var_name in suppress:
                val = suppress[var_name]
            else:
                val = getattr(self, var_name).replace('"', r'\"')
            lst_ret += [str_indent + f'{param_name}.{var_name} = "{val}"']

        if self.type in ["Task", "Bug"]:
            for var_name in ["estimated_time", "completed_time"]:
                if suppress and var_name in suppress:
                    val = suppress[var_name]
                else:
                    val = getattr(self, var_name)
                lst_ret += [str_indent + f"{param_name}.{var_name} = {val if val is None else(int(val))}"]

        return param_name, lst_ret

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
