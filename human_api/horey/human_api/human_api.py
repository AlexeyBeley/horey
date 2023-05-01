"""
Manage Azure Devops

"""
import datetime
from collections import defaultdict
from enum import Enum
from horey.h_logger import get_logger
from horey.human_api.human_api_configuration_policy import (
    HumanAPIConfigurationPolicy,
)
from horey.azure_devops_api.azure_devops_api import AzureDevopsAPI
from horey.azure_devops_api.azure_devops_api_configuration_policy import AzureDevopsAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class WorkObject:
    def __init__(self):
        self.id = None
        self.status = None
        self.created_date = None
        self.created_by = None
        self.assigned_to = None
        self.title = None
        self.sprint_id = None
        self.child_ids = []
        self.parent_ids = []
        self.related = []
        self.human_api_comment = None
        self.azure_devops_object = None

        self.children = []

    def init_from_azure_devops_work_item_base(self, work_item):
        """
        Init base attributes.

        :param work_item:
        :return:
        """

        self.azure_devops_work_item = work_item

        common_attributes = {"System.Id": self.init_default_attribute("id"),
                             "System.State": self.init_status_azure_devops,
                             "System.CreatedDate": self.init_created_date_azure_devops,
                             "System.CreatedBy": self.init_created_by_azure_devops,
                             "System.AssignedTo": self.init_assigned_to_azure_devops,
                             "System.Title": self.init_title_azure_devops,
                             "System.IterationPath": self.init_sprint_id_azure_devops
                             }

        for attribute_name, value in work_item.fields.items():
            if attribute_name in common_attributes:
                common_attributes[attribute_name](value)
        print(set(work_item.fields) - set(common_attributes))

        for relation in work_item.relations:
            if relation["rel"] in ["ArtifactLink", "AttachedFile", "Hyperlink", "Microsoft.VSTS.TestCase.SharedParameterReferencedBy-Forward"]:
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

    def init_created_by_azure_devops(self, value):
        self.created_by = value["uniqueName"]

    def init_assigned_to_azure_devops(self, value):
        self.assigned_to = value["uniqueName"]

    def init_title_azure_devops(self, value):
        self.title = value

    def init_sprint_id_azure_devops(self, value):
        self.sprint_id = value

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

    def generate_report_token(self):
        """
        Generate token to the daily report.

        :return:
        """
        return f"{CommonUtils.camel_case_to_snake_case(self.__class__.__name__)} {self.id} #{self.title}"


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

    def init_tasks_map(self, sprints=None):
        """
        Prepare tasks mapping.

        :return:
        """
        sprints = sprints if sprints is not None else []
        work_items = self.azure_devops_api.init_work_items_by_iterations(iterations_src=[sprint.azure_devops_object for sprint in sprints])
        self.init_tasks_from_azure_devops_work_items(work_items)
        self.init_tasks_relations()

    def init_tasks_from_azure_devops_work_items(self, work_items):
        """
        Init tasks map.

        :return:
        """

        for work_item in work_items:
            if work_item.work_item_type == "Feature":
                feature = Feature()
                feature.init_from_azure_devops_work_item(work_item)
                if feature.id in self.user_stories:
                    raise ValueError(f"feature id {feature.id} is already in use")
                self.features[feature.id] = feature
            elif work_item.work_item_type == "Epic":
                epic = Epic()
                epic.init_from_azure_devops_work_item(work_item)
                if epic.id in self.epics:
                    raise ValueError(f"epic id {epic.id} is already in use")
                self.epics[epic.id] = epic
            elif work_item.work_item_type == "User Story":
                user_story = UserStory()
                user_story.init_from_azure_devops_work_item(work_item)
                if user_story.id in self.user_stories:
                    raise ValueError(f"user_story id {user_story.id} is already in use")
                self.user_stories[user_story.id] = user_story
            elif work_item.work_item_type == "Bug":
                bug = Bug()
                bug.init_from_azure_devops_work_item(work_item)
                if bug.id in self.bugs:
                    raise ValueError(f"bug id {bug.id} is already in use")
                self.bugs[bug.id] = bug
            elif work_item.work_item_type == "Task":
                task = Task()
                task.init_from_azure_devops_work_item(work_item)
                if task.id in self.tasks:
                    raise ValueError(f"task id {task.id} is already in use")
                self.tasks[task.id] = task
            elif work_item.work_item_type is None:
                task = Task()
                task.id = work_item.id
                task.human_api_comment = str(work_item.dict_src)
                self.tasks[task.id] = task
            else:
                raise ValueError(f"Unknown work item type: {work_item.work_item_type}")

    def init_tasks_relations(self):
        """
        Init the objects' relations.

        :return:
        """
        tmp_dict = {}
        tmp_dict.update(self.features)
        tmp_dict.update(self.epics)
        tmp_dict.update(self.user_stories)
        tmp_dict.update(self.tasks)
        tmp_dict.update(self.bugs)

        for parent in self.features.values():
            for obj_id in parent.child_ids:
                parent.children.append(tmp_dict[obj_id])

        for parent in self.epics.values():
            for obj_id in parent.child_ids:
                parent.children.append(tmp_dict[obj_id])

        for parent in self.user_stories.values():
            for obj_id in parent.child_ids:
                parent.children.append(tmp_dict[obj_id])

        for parent in self.tasks.values():
            for obj_id in parent.child_ids:
                parent.children.append(tmp_dict[obj_id])

        for parent in self.bugs.values():
            for obj_id in parent.child_ids:
                parent.children.append(tmp_dict[obj_id])

    def get_sprint(self, date_find=None):
        """
        Find Sprint by date.

        :param date_find:
        :return:
        """

        iteration = self.azure_devops_api.get_iteration(from_cache=False, date_find=date_find)
        sprint = Sprint()
        sprint.init_from_azure_devops_iteration(iteration)
        return sprint

    def get_sprint_tasks_and_bugs(self, sprint: Sprint):
        """
        Get all work items of the sprint.

        :param sprint:
        :return:
        """

        tmp_dict = {}
        tmp_dict.update(self.tasks)
        tmp_dict.update(self.bugs)
        return [value for value in tmp_dict.values() if value.sprint_id == sprint.id]

    @staticmethod
    def split_by_worker(work_items):
        """
        Split work items by worker.

        :param work_items:
        :return:
        """

        ret = defaultdict(list)
        for work_item in work_items:
            ret[work_item.assigned_to].append(work_item)
        return ret

    def daily_report(self, output_file_path):
        """
        Init daily meeting area.

        :return:
        """
        sprint = self.get_sprint()

        self.init_tasks_map(sprints=[sprint])
        tmp_dict = {}
        tmp_dict.update(self.features)
        tmp_dict.update(self.epics)
        tmp_dict.update(self.user_stories)
        tmp_dict.update(self.tasks)
        tmp_dict.update(self.bugs)
        tmp_dict[-1] = UserStory()
        tmp_dict[-1].title = "Orphan"
        tmp_dict[-1].id = -1

        sprint_work_items = self.get_sprint_tasks_and_bugs(sprint)
        work_items_map = self.split_by_worker(sprint_work_items)
        str_ret = ""
        for worker_id, work_items in work_items_map.items():
            blocked = defaultdict(list)
            active = defaultdict(list)
            new = defaultdict(list)
            for work_item in work_items:
                if len(work_item.parent_ids) > 1:
                    raise ValueError(f"len(work_item.parent_ids) == {len(work_item.parent_ids)} != 1 ")

                if len(work_item.parent_ids) == 0:
                    parent_id = -1
                else:
                    parent_id = work_item.parent_ids[0]

                if work_item.status == work_item.Status.ACTIVE:
                    active[parent_id].append(work_item)
                elif work_item.status == work_item.Status.BLOCKED:
                    blocked[parent_id].append(work_item)
                elif work_item.status == work_item.Status.NEW:
                    new[parent_id].append(work_item)
                elif work_item.status != work_item.Status.CLOSED:
                    raise ValueError(f"Unknown status: {work_item.status}")
            str_ret += self.generate_worker_daily(tmp_dict, worker_id, new, active, blocked) + "\n"

        with open(output_file_path, "w") as file_handler:
            file_handler.write(str_ret)

    def daily_action(self, output_file_path):
        with open(output_file_path) as file_handler:
            str_src = file_handler.read()

        while "\n\n" in str_src:
            str_src = str_src.replace("\n\n", "\n")

        lst_per_worker = str_src.split("worker_id:")
        worker_report = lst_per_worker[7]
        actions = self.perform_worker_report_actions(worker_report)

        breakpoint()

    def perform_worker_report_actions(self, worker_report):
        """
        Split worker report to actions.

        :param worker_report:
        :return:
        """

        actions = []
        lst_worker_report = worker_report.split("\n")
        new_index = lst_worker_report.index(">NEW:")
        active_index = lst_worker_report.index(">ACTIVE:")
        blocked_index = lst_worker_report.index(">BLOCKED:")
        lines_new = lst_worker_report[new_index+1:active_index]
        lines_active = lst_worker_report[active_index+1:blocked_index]
        lines_blocked = lst_worker_report[blocked_index+1:]
        for line_src in lines_new:
            line_src = line_src.strip()
            parent_token = line_src[1:line_src.find("]")]
            line = line_src[len(parent_token):]
            line = line[line.find("->")+2:]
            line = line.strip()
            child_token = line[:line.rfind(":actions:")]
            action_token = line[len(child_token)+len(":actions:"):]
            actions = action_token.split(",")
            breakpoint()

            child_token_rep, child_token_title = child_token.split("#")
            child_token_rep = child_token_rep.strip()
            child_token_title = child_token_title.strip()
            if child_token_rep.startswith("task"):
                child_token_id = child_token_rep[len("task")+1:]
                if not child_token_id.isdigit():
                    breakpoint()
            elif child_token_rep.startswith("bug"):
                child_token_id = child_token_rep[len("bug")+1:]
            else:
                raise ValueError(f"Task identifier in '{line}'")

            for action in actions:
                action = action.strip()
                if action.startswith("+"):
                    breakpoint()
                    continue
                if action.startswith("comment"):
                    breakpoint()
                    continue
                if action.startswith("block"):
                    breakpoint()
                    continue
                if action.startswith("close"):
                    breakpoint()
                    continue
                if action.startswith("close"):
                    breakpoint()
                    continue


        breakpoint()
        return actions

    @staticmethod
    def generate_worker_daily(tmp_dict, worker_id, new, active, blocked):
        """
        Generate daily report.

        :param tmp_dict:
        :param worker_id:
        :param new:
        :param active:
        :param blocked:
        :return:
        """

        str_report = f"worker_id:{worker_id}\n"
        str_report += ">NEW:\n"
        for parent_id, items in new.items():
            for item in items:
                str_report += f"[{tmp_dict.get(parent_id).generate_report_token()}] -> {item.generate_report_token()} :actions:\n"

        str_report += "\n>ACTIVE:\n"
        for parent_id, items in active.items():
            for item in items:
                str_report += f"[{tmp_dict.get(parent_id).generate_report_token()}] -> {item.generate_report_token()} :actions:\n"

        str_report += "\n>BLOCKED:\n"
        for parent_id, items in blocked.items():
            for item in items:
                str_report += f"[{tmp_dict.get(parent_id).generate_report_token()}] -> {item.generate_report_token()} :actions:\n"

        str_report += "#"*len(str_report.split("\n")[-2]) + "\n"

        return str_report
