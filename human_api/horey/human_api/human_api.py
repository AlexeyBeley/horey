"""
Manage Azure Devops

"""
import datetime
from collections import defaultdict
from enum import Enum

import os
from horey.h_logger import get_logger
from horey.human_api.human_api_configuration_policy import (
    HumanAPIConfigurationPolicy,
)
from horey.azure_devops_api.azure_devops_api import AzureDevopsAPI
from horey.azure_devops_api.azure_devops_api_configuration_policy import AzureDevopsAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()

# pylint: disable= too-many-arguments
# pylint: disable= too-many-branches
# pylint: disable= too-many-locals
# pylint: disable= too-many-instance-attributes


class WorkObject:
    """
    Common data to all Work objects.
    """
    def __init__(self):
        self.id = None
        self.status = None
        self.created_date = None
        self.closed_date = None
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


class DailyReportAction:
    """
    Single task actions.
    """
    def __init__(self, line_src):
        self.parent_type = None
        self.parent_id = None
        self.parent_title = None

        self.child_type = None
        self.child_id = None
        self.child_title = None

        self.action_comment = None

        self.action_init_time = None
        self.action_add_time = None
        self.action_close = None
        self.action_activate = None
        self.action_block = None

        line_src = line_src.strip()
        parent_token = line_src[1:line_src.find("]")]
        line = line_src[len(parent_token):]
        line = line[line.find("->") + 2:]
        line = line.strip()
        child_token = line[:line.rfind(":actions:")].strip()
        action_token = line[len(child_token) + len(":actions:")+1:]
        self.init_parent(parent_token)
        self.init_child(child_token)
        self.init_actions(action_token)

    def init_child(self, child_token):
        """
        Child init from line

        :param child_token:
        :return:
        """

        child_token_rep, child_token_title = child_token.split("#")
        child_token_rep = child_token_rep.strip()
        self.child_title = child_token_title.strip()

        parts = child_token_rep.split(" ")
        if len(parts) == 0:
            parts = ["task", "0"]
        elif len(parts) == 1:
            if parts[0] in ["task", "bug"]:
                parts.append("0")
            else:
                parts = ["task"] + parts

        self.child_type, self.child_id = parts

        self.child_type = self.child_type.strip()
        if self.child_type not in ["task", "bug"]:
            raise RuntimeError(f"Task uid can not be parsed in: '{child_token}'")

        self.child_id = self.child_id.strip()
        if not self.child_id.isdigit():
            raise RuntimeError(f"Task uid can not be parsed in: '{child_token}'")

    def init_actions(self, action_token):
        """
        Init all actions.

        :param action_token:
        :return:
        """
        action_token = action_token.strip()

        if "end_comment" in action_token:
            commend_index = action_token.find("comment")
            end_comment_index = action_token.find("end_comment")
            comma_after_end_comment_index = action_token.find(",", end_comment_index)
            comma_after_end_comment_index = len(action_token) if comma_after_end_comment_index == -1 else comma_after_end_comment_index

            self.action_comment = action_token[commend_index+len("comment"): end_comment_index].strip()
            action_token = action_token[:commend_index] + action_token[comma_after_end_comment_index:]
            action_token = action_token.strip()
            action_token = action_token.strip(" ,")

        actions = action_token.split(",")

        for action in actions:
            action = action.strip()
            if action.startswith("+"):
                if not action[1:].isdigit():
                    raise RuntimeError(f"Can not parse action: '{action_token}'")
                self.action_add_time = int(action[1:])
                continue
            if action.startswith("comment"):
                self.action_comment = action[len("comment"):].strip()
                continue
            if action.startswith("block"):
                self.action_block = True
                continue
            if action.startswith("close"):
                self.action_close = True
                continue

    def init_parent(self, parent_token):
        """
        Init parent from line.

        :param parent_token:
        :return:
        """
        logger.info(f"Initializing parent token: {parent_token}")
        uid, self.parent_title = parent_token.split("#")
        self.parent_title = self.parent_title.strip()
        uid = uid.strip()
        parts = uid.split(" ")
        if len(parts) < 2:
            if len(parts) == 0:
                parts = ["user_story", "0"]
            elif parts[0] == "-1" or parts[0].isdigit():
                parts = ["user_story"] + parts
            else:
                parts.append("0")

        self.parent_type, self.parent_id = parts
        if self.parent_id != "-1" and not self.parent_id.isdigit():
            raise ValueError(f"Work item id must be either digit or '-1', received: '{parent_token}'")

        if self.parent_type not in ["user_story"]:
            raise ValueError(f"Unknown worker type in '{parent_token}'")


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

    def get_sprints(self, date_find=None, sprint_names=None):
        """
        Find Sprint by date.

        :param sprint_names:
        :param date_find:
        :return:
        """
        lst_ret = []
        for iteration in self.azure_devops_api.get_iterations(from_cache=False, date_find=date_find, iteration_names=sprint_names):
            sprint = Sprint()
            sprint.init_from_azure_devops_iteration(iteration)
            lst_ret.append(sprint)
        return lst_ret

    def get_sprint_tasks_and_bugs(self, sprints):
        """
        Get all work items of the sprint.

        :param sprints:
        :return:
        """

        tmp_dict = {}
        tmp_dict.update(self.tasks)
        tmp_dict.update(self.bugs)
        sprint_ids = [sprint.id for sprint in sprints]
        return [value for value in tmp_dict.values() if value.sprint_id in sprint_ids]

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

    def daily_report(self, output_file_path, protected_output_file_path, sprint_name=None):
        """
        Init daily meeting area.

        :return:
        """
        sprints = self.get_sprints(sprint_names=[sprint_name])

        self.init_tasks_map(sprints=sprints)
        tmp_dict = {}
        tmp_dict.update(self.features)
        tmp_dict.update(self.epics)
        tmp_dict.update(self.user_stories)
        tmp_dict.update(self.tasks)
        tmp_dict.update(self.bugs)
        tmp_dict[-1] = UserStory()
        tmp_dict[-1].title = "Orphan"
        tmp_dict[-1].id = -1

        sprint_work_items = self.get_sprint_tasks_and_bugs(sprints)
        work_items_map = self.split_by_worker(sprint_work_items)
        str_ret = ""
        for worker_id, work_items in work_items_map.items():
            blocked = defaultdict(list)
            active = defaultdict(list)
            new = defaultdict(list)
            closed = defaultdict(list)
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
                elif work_item.status == work_item.Status.CLOSED:
                    if work_item.closed_date >= datetime.datetime.now() - datetime.timedelta(days=3):
                        closed[parent_id].append(work_item)
                else:
                    raise ValueError(f"Unknown status: {work_item.status}")
            str_ret += self.generate_worker_daily(tmp_dict, worker_id, new, active, blocked, closed) + "\n"

        with open(output_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(str_ret)

        if not os.path.exists(protected_output_file_path):
            with open(protected_output_file_path, "w", encoding="utf-8") as file_handler:
                file_handler.write(str_ret)

    def daily_action(self, input_file_path, sprint_name):
        """
        Perform daily ritual - do the changes in the tasks' management system and
        generate YTB report.

        :param input_file_path:
        :return:
        """
        with open(input_file_path, encoding="utf-8") as file_handler:
            str_src = file_handler.read()

        while "\n\n" in str_src:
            str_src = str_src.replace("\n\n", "\n")

        lst_per_worker = str_src.split("worker_id:")
        str_ret = ""
        for worker_report in lst_per_worker:
            if not worker_report.strip():
                continue
            str_ret += self.perform_worker_report_actions(worker_report, sprint_name)
            str_ret += "#"*100 + "\n"

        logger.info(str_ret)

    def perform_worker_report_actions(self, worker_report, sprint_name):
        """
        Split worker report to actions.

        :param worker_report:
        :return:
        """
        lst_worker_report = worker_report.split("\n")
        index_end = lst_worker_report.index("#"*100)
        lst_worker_report = lst_worker_report[:index_end]

        new_index = lst_worker_report.index(">NEW:")
        active_index = lst_worker_report.index(">ACTIVE:")
        blocked_index = lst_worker_report.index(">BLOCKED:")
        closed_index = lst_worker_report.index(">CLOSED:")
        lines_new = lst_worker_report[new_index+1:active_index]
        lines_active = lst_worker_report[active_index+1:blocked_index]
        lines_blocked = lst_worker_report[blocked_index + 1:closed_index]
        lines_closed = lst_worker_report[closed_index+1:]

        actions_new = [DailyReportAction(line_src) for line_src in lines_new]
        actions_active = [DailyReportAction(line_src) for line_src in lines_active]
        actions_blocked = [DailyReportAction(line_src) for line_src in lines_blocked]
        actions_closed = [DailyReportAction(line_src) for line_src in lines_closed]

        self.perform_task_management_system_changes(sprint_name, actions_new, actions_active, actions_blocked, actions_closed)
        name = lst_worker_report[0].lower()
        name = name[:name.index("@")]
        ytb_report = self.generate_ytb_report(actions_new, actions_active, actions_blocked, actions_closed)
        return f"{name}\n{ytb_report}"

    def perform_task_management_system_changes(self, sprint_name, actions_new, actions_active, actions_blocked, actions_closed):
        """
        Perform the changes using API

        :param actions_new:
        :param actions_active:
        :param actions_blocked:
        :param actions_closed:
        :return:
        """

        parents_to_actions_map = defaultdict(list)
        for action in actions_new + actions_active + actions_blocked + actions_closed:
            if action.parent_id == "0":
                parents_to_actions_map[action.parent_title].append(action)

        for parent_title, actions in parents_to_actions_map.items():
            user_story_id = self.azure_devops_api.provision_work_item_by_params(actions[0].parent_type, parent_title, iteration_partial_path=sprint_name)
            for action in actions:
                action.parent_id = user_story_id

        for action in actions_new + actions_active + actions_blocked + actions_closed:
            if action.child_id == "0":
                action.child_id = self.azure_devops_api.provision_work_item_by_params(action.child_type, action.child_title, iteration_partial_path=sprint_name, original_estimate_time=action.action_init_time)
                if action.parent_id != "-1":
                    logger.warning(f"Set manually workitem {action.child_id} parent to {action.parent_id}")

        for action in actions_active:
            if action.action_add_time is not None:
                self.azure_devops_api.add_hours_to_work_item(action.child_id,  action.action_add_time)

    def action_to_ytb_report_line(self, action):
        """
        Single line formatter.

        :param action:
        :return:
        """
        return f"[{action.parent_id}-{action.parent_title}] -> {action.child_id}-{action.child_title}"

    def generate_ytb_report(self, actions_new, actions_active, actions_blocked, actions_closed):
        """
        YTB report formatter for a single user.

        :param actions_new:
        :param actions_active:
        :param actions_blocked:
        :param actions_closed:
        :return:
        """
        str_ret = "Y:\n"
        y_report = [action for action in actions_new + actions_active + actions_blocked + actions_closed if action.action_add_time]
        str_ret += "\n".join([self.action_to_ytb_report_line(action) for action in y_report])
        str_ret += "\nT:\n"
        str_ret += "\n".join([self.action_to_ytb_report_line(action) for action in actions_active if not action.action_close])
        str_ret += "\nB:\n"
        str_ret += "\n".join([self.action_to_ytb_report_line(action) for action in actions_new + actions_active + actions_blocked + actions_closed if action.action_block])
        while "\n\n" in str_ret:
            str_ret = str_ret.replace("\n\n", "\n")
        return str_ret

    @staticmethod
    def generate_worker_daily(tmp_dict, worker_id, new, active, blocked, closed):
        """
        Generate daily report.

        :param tmp_dict:
        :param worker_id:
        :param new:
        :param active:
        :param blocked:
        :param closed:
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

        str_report += "\n>CLOSED:\n"
        for parent_id, items in closed.items():
            for item in items:
                str_report += f"[{tmp_dict.get(parent_id).generate_report_token()}] -> {item.generate_report_token()} :actions:\n"

        str_report += "#"*100 + "\n"

        return str_report
