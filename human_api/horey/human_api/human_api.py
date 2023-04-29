"""
Manage Azure Devops

"""
import datetime
from enum import Enum
from horey.h_logger import get_logger
from horey.human_api.human_api_configuration_policy import (
    HumanAPIConfigurationPolicy,
)
from horey.azure_devops_api.azure_devops_api import AzureDevopsAPI
from horey.azure_devops_api.azure_devops_api_configuration_policy import AzureDevopsAPIConfigurationPolicy

logger = get_logger()


class WorkObject:
    def __init__(self):
        self.id = None
        self.status = None
        self.created_date = None
        self.created_by = None
        self.assigned_to = None
        self.title = None
        self.iteration_id = None
        self.child_ids = []
        self.parent_ids = []
        self.related = []

        self.children = []

    def init_from_azure_devops_work_item_base(self, work_item):
        """
        Init base attributes.

        :param work_item:
        :return:
        """

        common_attributes = {"System.Id": self.init_default_attribute("id"),
                             "System.State": self.init_status_azure_devops,
                             "System.CreatedDate": self.init_created_date_azure_devops,
                             "System.CreatedBy": self.init_created_by_azure_devops,
                             "System.AssignedTo": self.init_assigned_to_azure_devops,
                             "System.Title": self.init_title_azure_devops,
                             "System.IterationPath": self.init_iteration_id_azure_devops
                             }

        for attribute_name, value in work_item.fields.items():
            if attribute_name in common_attributes:
                common_attributes[attribute_name](value)
        print(set(work_item.fields) - set(common_attributes))

        for relation in work_item.relations:
            if relation["attributes"]["name"] == "Child":
                self.child_ids.append(int(relation["url"].split("/")[-1]))
            elif relation["attributes"]["name"] == "Parent":
                self.parent_ids.append(int(relation["url"].split("/")[-1]))
            elif relation["attributes"]["name"] in ["Related", "Duplicate Of", "Duplicate", "Successor", "Predecessor"]:
                self.related.append(relation)
            elif relation["rel"] in ["AttachedFile", "Hyperlink"]:
                self.related.append(relation)
            else:
                raise ValueError(f"Unknown relation name in: '{relation}': {relation['attributes']['name']}")

    def init_default_attribute(self, attribute_name):
        return lambda value: setattr(self, attribute_name, value)

    def init_status_azure_devops(self, value):
        """
        Translate azure_devops state to human_api status.

        :param value:
        :return:
        """

        if value == "New":
            self.status = self.Status.NEW
        elif value == "On Hold":
            self.status = self.Status.BLOCKED
        elif value == "Pending Deployment":
            self.status = self.Status.BLOCKED
        elif value == "Active":
            self.status = self.Status.ACTIVE
        elif value == "PM Review":
            self.status = self.Status.BLOCKED
        elif value == "Resolved":
            self.status = self.Status.CLOSED
        else:
            raise ValueError(f"Status unknown: {value}")

    def init_created_by_azure_devops(self, value):
        self.created_by = value["uniqueName"]

    def init_assigned_to_azure_devops(self, value):
        self.assigned_to = value["uniqueName"]

    def init_title_azure_devops(self, value):
        self.title = value

    def init_iteration_id_azure_devops(self, value):
        self.iteration_id = value

    def init_created_date_azure_devops(self, value):
        if "." in value:
            self.created_date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self.created_date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")

    class Status(Enum):
        NEW = "NEW"
        ACTIVE = "ACTIVE"
        BLOCKED = "BLOCKED"
        CLOSED = "CLOSED"


class Task(WorkObject):
    """
    Work item -task, user story, feature, epic etc.
    """

    def print(self):
        """
        Print the fields.

        :return:
        """

        for field_name, field_value in self.fields.items():
            print(f"--> {field_name}: {field_value}")

    def init_from_azure_devops_work_item(self, work_item):
        """
        Init self from azure_devops work item
        :param work_item:
        :return:
        """
        self.init_from_azure_devops_work_item_base(work_item)


class Feature(WorkObject):
    """
    Feature
    """

    def print(self):
        """
        Print the fields.

        :return:
        """
        breakpoint()

    def init_from_azure_devops_work_item(self, work_item):
        """
        Init self from azure_devops work item
        :param work_item:
        :return:
        """
        self.init_from_azure_devops_work_item_base(work_item)


class Epic(WorkObject):
    """
    Feature
    """

    def print(self):
        """
        Print the fields.

        :return:
        """
        breakpoint()

    def init_from_azure_devops_work_item(self, work_item):
        """
        Init self from azure_devops work item
        :param work_item:
        :return:
        """
        self.init_from_azure_devops_work_item_base(work_item)


class UserStory(WorkObject):
    """
    Feature
    """

    def print(self):
        """
        Print the fields.

        :return:
        """
        breakpoint()

    def init_from_azure_devops_work_item(self, work_item):
        """
        Init self from azure_devops work item
        :param work_item:
        :return:
        """
        self.init_from_azure_devops_work_item_base(work_item)


class Bug(WorkObject):
    """
    Feature
    """

    def print(self):
        """
        Print the fields.

        :return:
        """
        breakpoint()

    def init_from_azure_devops_work_item(self, work_item):
        """
        Init self from azure_devops work item
        :param work_item:
        :return:
        """
        self.init_from_azure_devops_work_item_base(work_item)


class Sprint:
    """
    Single iteration

    """

    def __init__(self):
        breakpoint()


class HumanAPI:
    """
    Main class
    """
    def __init__(self, configuration: HumanAPIConfigurationPolicy = None):
        self.features = {}
        self.epics = {}
        self.user_stories = {}
        self.bugs = {}
        self.tasks = {}
        self.configuration = configuration
        azure_devops_api_config = AzureDevopsAPIConfigurationPolicy()
        azure_devops_api_config.configuration_file_full_path = self.configuration.azure_devops_api_configuration_file_path
        azure_devops_api_config.init_from_file()
        self.azure_devops_api = AzureDevopsAPI(azure_devops_api_config)

    def init_tasks_map(self):
        """
        Prepare tasks mapping.

        :return:
        """
        self.init_tasks_from_azure_devops_work_items()
        self.init_tasks_relations()

    def init_tasks_from_azure_devops_work_items(self):
        """
        Init tasks map.

        :return:
        """

        self.azure_devops_api.init_work_items(cache_file_path="/Users/alexey.beley/git/ignore/azure_devops/work_items.json")
        for work_item in self.azure_devops_api.work_items:
            if work_item.dict_src["fields"]["System.WorkItemType"] == "Feature":
                feature = Feature()
                feature.init_from_azure_devops_work_item(work_item)
                if feature.id in self.user_stories:
                    raise ValueError(f"feature id {feature.id} is already in use")
                self.features[feature.id] = feature
            elif work_item.dict_src["fields"]["System.WorkItemType"] == "Epic":
                epic = Epic()
                epic.init_from_azure_devops_work_item(work_item)
                if epic.id in self.epics:
                    raise ValueError(f"epic id {epic.id} is already in use")
                self.epics[epic.id] = epic
            elif work_item.dict_src["fields"]["System.WorkItemType"] == "User Story":
                user_story = UserStory()
                user_story.init_from_azure_devops_work_item(work_item)
                if user_story.id in self.user_stories:
                    raise ValueError(f"user_story id {user_story.id} is already in use")
                self.user_stories[user_story.id] = user_story
            elif work_item.dict_src["fields"]["System.WorkItemType"] == "Bug":
                bug = Bug()
                bug.init_from_azure_devops_work_item(work_item)
                if bug.id in self.bugs:
                    raise ValueError(f"bug id {bug.id} is already in use")
                self.bugs[bug.id] = bug
            elif work_item.dict_src["fields"]["System.WorkItemType"] == "Task":
                task = Task()
                task.init_from_azure_devops_work_item(work_item)
                if task.id in self.tasks:
                    raise ValueError(f"task id {task.id} is already in use")
                self.tasks[task.id] = task
            else:
                raise ValueError(f'Unknown work item type: {work_item.dict_src["fields"]["System.WorkItemType"]}')

    def init_tasks_relations(self):
        """
        Init the objects' relations.

        :return:
        """
        tmp_dict = {key: value for key, value in self.features.items()}
        tmp_dict.update(self.epics)
        tmp_dict.update(self.user_stories)
        tmp_dict.update(self.tasks)
        tmp_dict.update(self.bugs)

        for feature in self.features.values():
            for obj_id in feature.child_ids:
                if obj_id not in tmp_dict:
                    breakpoint()
                feature.children.append(tmp_dict[obj_id])
        breakpoint()

    def init_daily_meeting(self):
        """
        Init daily meeting area.

        :return:
        """
        breakpoint()
        self.azure_devops_api.init_work_items()
        current_iteration = self.azure_devops_api.get_iteration()
        iteration_work_items = self.azure_devops_api.get_iteration_work_items(current_iteration)

        work_items_map = self.azure_devops_api.split_work_items_by_worker(iteration_work_items)
        for worker_name, work_items in work_items_map.items():
            blockers = []
            active = []
            new = []
            for work_item in work_items:
                if work_item.dict_src["fields"]["System.State"] == "New":
                    new.append(work_item)
                    breakpoint()
                elif work_item.dict_src["fields"]["System.State"] == "On Hold":
                    blockers.append(work_item)
                elif work_item.dict_src["fields"]["System.State"] == "Pending Deployment":
                    blockers.append(work_item)
                elif work_item.dict_src["fields"]["System.State"] == "Active":
                    active.append(work_item)
                elif work_item.dict_src["fields"]["System.State"] == "PM Review":
                    blockers.append(work_item)
                elif work_item.dict_src["fields"]["System.State"] == "Resolved":
                    continue

                raise ValueError(f'Unknown state: {work_item.dict_src["fields"]["System.State"]}')
