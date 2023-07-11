"""
Common parent to all work.
"""
import datetime
from enum import Enum
from horey.common_utils.common_utils import CommonUtils


# pylint: disable= too-many-instance-attributes
class WorkObject:
    """
    Common data to all Work objects.
    """

    def __init__(self):
        self.id = None
        self.status = None
        self.created_date = None
        self._closed_date = None
        self.state_change_date = None
        self.created_by = None
        self.assigned_to = None
        self.title = None
        self.sprint_id = None
        self.child_ids = []
        self.parent_ids = []
        self.children = []
        self.related = []
        self.human_api_comment = None
        self.azure_devops_object = None
        self.time_estimation = None

        self.children = []
        self._dod = None

    @property
    def dod(self):
        """
        Definition Of Done.

        :return:
        """
        if self._dod is None:
            self._dod = self.state_change_date
        return self._dod

    @dod.setter
    def dod(self, value):
        self._dod = value

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

    def init_from_azure_devops_work_item_base(self, work_item):
        """
        Init base attributes.

        :param work_item:
        :return:
        """

        self.azure_devops_object = work_item

        common_attributes = {"System.Id": self.init_default_attribute("id"),
                             "System.State": self.init_status_azure_devops,
                             "System.CreatedDate": self.init_created_date_azure_devops,
                             "System.CreatedBy": self.init_created_by_azure_devops,
                             "System.AssignedTo": self.init_assigned_to_azure_devops,
                             "System.Title": self.init_title_azure_devops,
                             "System.IterationPath": self.init_sprint_id_azure_devops,
                             "Microsoft.VSTS.Common.ClosedDate": self.init_closed_date_azure_devops,
                             "Microsoft.VSTS.Common.ResolvedDate": self.init_closed_date_azure_devops,
                             "Microsoft.VSTS.Common.StateChangeDate": self.init_state_change_date_azure_devops,
                             }

        for attribute_name, value in work_item.fields.items():
            if attribute_name in common_attributes:
                common_attributes[attribute_name](value)
        print(set(work_item.fields) - set(common_attributes))

        for relation in work_item.relations:
            if relation["rel"] in ["ArtifactLink", "AttachedFile", "Hyperlink",
                                   "Microsoft.VSTS.TestCase.SharedParameterReferencedBy-Forward"]:
                self.related.append(relation)
            elif relation["attributes"]["name"] == "Child":
                self.child_ids.append(int(relation["url"].split("/")[-1]))
            elif relation["attributes"]["name"] == "Parent":
                self.parent_ids.append(int(relation["url"].split("/")[-1]))
            elif relation["attributes"]["name"] in ["Related", "Duplicate Of", "Duplicate", "Successor", "Predecessor"]:
                self.related.append(relation)
            else:
                raise ValueError(f"Unknown relation name in: '{relation}': '{relation['attributes']['name']}'")

    def init_default_attribute(self, attribute_name):
        """
        Init vanilla as is.

        :param attribute_name:
        :return:
        """
        return lambda value: setattr(self, attribute_name, value)

    def init_status_azure_devops(self, value):
        """
        Translate azure_devops state to human_api status.

        :param value:
        :return:
        """

        if value == "New":
            self.status = self.Status.NEW
        elif value in ["On Hold", "Pending Deployment", "PM Review"]:
            self.status = self.Status.BLOCKED
        elif value == "Active":
            self.status = self.Status.ACTIVE
        elif value in ["Resolved", "Closed", "Removed"]:
            self.status = self.Status.CLOSED
        else:
            raise ValueError(f"Status unknown: {value}")

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

    def init_created_by_azure_devops(self, value):
        """
        Init from azure devops object.
        :param value:
        :return:
        """
        self.created_by = value["uniqueName"]

    def init_assigned_to_azure_devops(self, value):
        """
        Init from azure devops object.
        :param value:
        :return:
        """
        self.assigned_to = value["uniqueName"]

    def init_title_azure_devops(self, value):
        """
        Init from azure devops object.
        :param value:
        :return:
        """
        self.title = value

    def init_sprint_id_azure_devops(self, value):
        """
        Init from azure devops object.
        :param value:
        :return:
        """
        self.sprint_id = value

    def init_closed_date_azure_devops(self, value):
        """
        Init from azure devops object.

        :param value:
        :return:
        """
        if "." in value:
            self.closed_date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self.closed_date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")

    def init_state_change_date_azure_devops(self, value):
        """
        Init from azure devops object.

        :param value:
        :return:
        """
        if "." in value:
            self.state_change_date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self.state_change_date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")

    def init_created_date_azure_devops(self, value):
        """
        Init from azure devops object.
        :param value:
        :return:
        """
        if "." in value:
            self.created_date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self.created_date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")

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
        return f"{CommonUtils.camel_case_to_snake_case(self.__class__.__name__)} {self.id} #{self.title}"

    def add(self, child):
        """
        Add a child.

        :param child:
        :return:
        """

        self.children.append(child)
