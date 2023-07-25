"""
Manage Azure Devops

"""
import copy
import json
import logging
import datetime
from collections import defaultdict

import os
from horey.h_logger import get_logger
from horey.h_logger.h_logger import formatter
from horey.human_api.human_api_configuration_policy import (
    HumanAPIConfigurationPolicy,
)
from horey.human_api.work_object import WorkObject
from horey.human_api.task import Task
from horey.human_api.bug import Bug
from horey.human_api.epic import Epic
from horey.human_api.feature import Feature
from horey.human_api.user_story import UserStory
from horey.human_api.sprint import Sprint

from horey.azure_devops_api.azure_devops_api import AzureDevopsAPI
from horey.azure_devops_api.azure_devops_api_configuration_policy import AzureDevopsAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils
from horey.common_utils.text_block import TextBlock

logger = get_logger()


# pylint: disable= too-many-lines
# pylint: disable= too-many-arguments
# pylint: disable= too-many-branches
# pylint: disable= too-many-locals
# pylint: disable= too-many-instance-attributes

class DailyReportAction:
    """
    Single task actions.
    """

    def __init__(self, line_src):
        self.src_line = line_src
        self.init_errors = []
        self.parent_type = None
        self.parent_id = None
        self.parent_title = None

        self.child_type = None
        self.child_id = None
        self.child_title = None

        self._action_comment = None

        self.action_init_time = None
        self._action_add_time = None
        self.action_new = None
        self.action_close = None
        self.action_activate = None
        self.action_block = None

        line_src = line_src.strip()
        parent_token = line_src[1:line_src.find("]")].strip(" ")
        line = line_src[len(parent_token):]
        line = line[line.find("->") + 2:]
        line = line.strip()
        child_token = line[:line.rfind(":actions:")]
        action_token = line[len(child_token) + len(":actions:") + 1:]
        child_token = child_token.strip()
        self.init_parent(parent_token)
        self.init_child(child_token)
        self.init_actions(action_token)

    @property
    def action_comment(self):
        """
        action_comment getter.

        :return:
        """

        return self._action_comment

    @action_comment.setter
    def action_comment(self, value):
        value = value[0].upper() + value[1:]
        if self.action_add_time is not None:
            value = f"Worked for {self.action_add_time} hours:\n" + value
        self._action_comment = value

    @property
    def action_add_time(self):
        """
        action_add_time getter.

        :return:
        """

        return self._action_add_time

    @action_add_time.setter
    def action_add_time(self, value):
        self._action_add_time = value
        if self.action_comment is not None:
            self.action_comment = f"Worked for {value} hours:\n" + self.action_comment

    def init_child(self, child_token):
        """
        Child init from line

        :param child_token:
        :return:
        """

        logger.info(f"Initializing child token: {child_token}")
        child_token_rep, child_token_title = child_token.split("#")
        child_token_rep = child_token_rep.strip()
        self.child_title = child_token_title.strip()

        parts = child_token_rep.split(" ")
        if len(parts) == 0:
            parts = ["Task", "0"]
        elif len(parts) == 1:
            if parts[0] in ["Task", "Bug"]:
                parts.append("0")
            else:
                parts = ["Task"] + parts

        self.child_type, self.child_id = parts

        self.child_type = self.child_type.strip()
        if self.child_type not in ["Task", "Bug"]:
            self.init_errors.append(f"Task uid can not be parsed in: '{child_token}'")

        self.child_id = self.child_id.strip()
        if not self.child_id.isdigit():
            self.init_errors.append(f"Task uid can not be parsed in: '{child_token}'")

    def init_actions(self, action_token):
        """
        Init all actions.

        :param action_token:
        :return:
        """
        action_token = action_token.strip()
        if action_token == "":
            return

        if "end_comment" in action_token:
            commend_index = action_token.find("comment")
            end_comment_index = action_token.find("end_comment")
            comma_after_end_comment_index = action_token.find(",", end_comment_index)
            comma_after_end_comment_index = len(
                action_token) if comma_after_end_comment_index == -1 else comma_after_end_comment_index

            self.action_comment = action_token[commend_index + len("comment"): end_comment_index].strip()
            action_token = action_token[:commend_index] + action_token[comma_after_end_comment_index:]
            action_token = action_token.strip()
            action_token = action_token.strip(" ,")

        actions = action_token.split(",")

        for action in actions:
            action = action.strip()
            if action.startswith("+"):
                logger.info(f"Initializing '+' action token: {action}")
                if not action[1:].isdigit():
                    self.init_errors.append(f"Can not parse action: '{action_token}'")
                try:
                    self.action_add_time = int(action[1:])
                except ValueError as error_inst:
                    self.init_errors.append(repr(error_inst))
                continue
            if action.startswith("comment"):
                self.action_comment = action[len("comment"):].strip()
                continue
            if action.startswith("block"):
                self.action_block = True
                continue
            if action.startswith("activ"):
                self.action_activate = True
                continue
            if action.startswith("close"):
                self.action_close = True
                continue
            if action.startswith("new"):
                self.action_new = True
                continue
            if action.isdigit():
                self.action_init_time = int(action)
                continue
            self.init_errors.append(f"Unknown action '{action}' in line '{self.src_line}'")

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
                parts = ["UserStory", "0"]
            elif parts[0] == "-1" or parts[0].isdigit():
                parts = ["UserStory"] + parts
            else:
                parts.append("0")

        self.parent_type, self.parent_id = parts
        if self.parent_id != "-1" and not self.parent_id.isdigit():
            raise ValueError(f"Work item id must be either digit or '-1', received: '{parent_token}'")

        if self.parent_type not in ["UserStory", "Bug", "Task"]:
            raise ValueError(f"Unknown Parent WIT type '{self.parent_type}' in '{parent_token}'")


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
        self.provisioned_new_parents_map = {}
        self.configuration = configuration
        if configuration is not None:
            azure_devops_api_config = AzureDevopsAPIConfigurationPolicy()
            azure_devops_api_config.configuration_file_full_path = self.configuration.azure_devops_api_configuration_file_path
            azure_devops_api_config.init_from_file()
            self.azure_devops_api = AzureDevopsAPI(azure_devops_api_config)
            os.makedirs(self.configuration.daily_dir_path, exist_ok=True)

            file_handler = logging.FileHandler(os.path.join(self.configuration.daily_dir_path, "human_api.log"))
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)

    def init_tasks_map(self, sprints=None):
        """
        Prepare tasks mapping.

        :return:
        """

        #with open("./tmp_cache.json") as fh:
        #    work_objects = json.load(fh)

        sprints = sprints if sprints is not None else []
        work_objects = self.azure_devops_api.init_work_items_by_iterations(
            iteration_names=[sprint.name for sprint in sprints])

        with open("./tmp_cache.json", "w", encoding="utf-8") as fh:
            json.dump(work_objects, fh)

        self.init_work_objects_from_dicts(work_objects)

    def init_work_objects_from_dicts(self, work_objects_dicts):
        """
        Init self work objects

        :param work_objects_dicts:
        :return:
        """

        for obj in self.generate_work_objects_from_dicts(work_objects_dicts):
            if obj.type == "Feature":
                if obj.id in self.features:
                    raise ValueError(f"Feature id {obj.id} is already in use")
                self.features[obj.id] = obj
            elif obj.type == "Epic":
                if obj.id in self.epics:
                    raise ValueError(f"Epic id {obj.id} is already in use")
                self.epics[obj.id] = obj
            elif obj.type == "UserStory":
                if obj.id in self.user_stories:
                    raise ValueError(f"UserStory id {obj.id} is already in use")
                self.user_stories[obj.id] = obj
            elif obj.type == "Bug":
                if obj.id in self.bugs:
                    raise ValueError(f"Bug id {obj.id} is already in use")
                self.bugs[obj.id] = obj
            elif obj.type == "Task":
                if obj.id in self.tasks:
                    raise ValueError(f"Task id {obj.id} is already in use")
                self.tasks[obj.id] = obj
            else:
                raise ValueError(f"Unknown work object type: {obj.type}")
    @staticmethod
    def generate_work_objects_from_dicts(work_objects_dicts):
        """
        Generate work objects from dicts

        :return:
        """

        lst_ret = []

        for work_item in work_objects_dicts:
            if work_item["type"] == "Feature":
                feature = Feature()
                feature.init_from_dict(work_item)
                lst_ret.append(feature)
            elif work_item["type"] == "Epic":
                epic = Epic()
                epic.init_from_dict(work_item)
                lst_ret.append(epic)
            elif work_item["type"] == "UserStory":
                user_story = UserStory()
                user_story.init_from_dict(work_item)
                lst_ret.append(user_story)
            elif work_item["type"] == "Bug":
                bug = Bug()
                bug.init_from_dict(work_item)
                lst_ret.append(bug)
            elif work_item["type"] == "Task":
                task = Task()
                task.init_from_dict(work_item)
                lst_ret.append(task)
            else:
                raise ValueError(f"Unknown work item type: {work_item.work_item_type}")

        return lst_ret

    def init_tasks_relations(self):
        """
        Init the objects' relations.

        :return:
        # todo: remove
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
        for iteration in self.azure_devops_api.get_iterations(from_cache=False, date_find=date_find,
                                                              iteration_pathes=sprint_names):
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

        sprint_names = [sprint.name for sprint in sprints]
        return [value for value in {**self.tasks, **self.bugs}.values() if value.sprint_name in sprint_names]

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

    def daily_report(self):
        """
        Init daily meeting area.

        :return:
        """
        sprints = self.get_sprints(sprint_names=[self.configuration.sprint_name])

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

        str_ret = str_ret.strip("\n\n") + "\n"
        with open(self.configuration.daily_hapi_file_path, "w", encoding="utf-8") as file_handler:
            file_handler.write(str_ret)

        if not os.path.exists(self.configuration.protected_input_file_path):
            with open(self.configuration.protected_input_file_path, "w", encoding="utf-8") as file_handler:
                file_handler.write(str_ret)

    def generate_daily_hr(self):
        """
        Generate a human-readable daily report.

        :return:
        """

        input_actions_per_worker_map = self.init_actions_from_report_file(self.configuration.protected_input_file_path)
        base_actions_per_worker_map = self.init_actions_from_report_file(self.configuration.daily_hapi_file_path)

        str_ret = ""
        for worker_name, input_actions in input_actions_per_worker_map.items():
            str_ret_tmp = self.generate_daily_hr_per_worker(input_actions,
                                                          base_actions_per_worker_map[worker_name])

            if str_ret_tmp == ">NEW:\n>ACTIVE:\n>BLOCKED:\n>CLOSED:":
                continue

            str_ret += "\n" + worker_name + "\n" + str_ret_tmp + "\n"

        with open(self.configuration.daily_hr_output_file_path, "a", encoding="utf-8") as file_handler:
            file_handler.write(str_ret)

    def generate_daily_hr_per_worker(self, input_actions, base_actions):
        """

        :param input_actions:
        :param base_actions:
        :return:
        """
        ret = ">NEW:\n" + self.generate_daily_hr_per_action_block(input_actions["actions_new"], base_actions["actions_new"])
        ret += "\n>ACTIVE:\n" + self.generate_daily_hr_per_action_block(input_actions["actions_active"], base_actions["actions_active"])
        ret += "\n>BLOCKED:\n" + "\n".join(action.src_line for action in input_actions["actions_blocked"])
        ret += "\n>CLOSED:\n" + self.generate_daily_hr_per_action_block(input_actions["actions_closed"], base_actions["actions_closed"])

        return ret.replace("\n\n", "\n").strip("\n")

    def generate_daily_hr_per_action_block(self, input_actions, base_actions):
        """
        Find differences per action's block

        :param input_actions:
        :param base_actions:
        :return:
        """

        str_ret = ""
        input_map = {(action.parent_title, action.child_title): action.src_line for action in input_actions}
        base_map = {(action.parent_title, action.child_title): action.src_line for action in base_actions}
        for input_pair, input_line in input_map.items():
            if input_pair not in base_map:
                str_ret += input_line + "\n"
                continue
            if input_line != base_map[input_pair]:
                str_ret += input_line + "\n"
                continue
        return str_ret

    def daily_action(self):
        """
        Perform daily ritual - do the changes in the tasks' management system and
        generate YTB report.

        :return:
        """
        if os.path.exists(self.configuration.output_file_path):
            raise RuntimeError(f"Looks like you've already run the daily action. "
                               f"Output file at: {self.configuration.output_file_path}")
        input_actions_per_worker_map = self.init_actions_from_report_file(self.configuration.protected_input_file_path)
        base_actions_per_worker_map = self.init_actions_from_report_file(self.configuration.daily_hapi_file_path)

        str_ret = ""
        for worker_name, input_actions in input_actions_per_worker_map.items():
            str_ret += self.perform_worker_report_actions(worker_name, input_actions,
                                                          base_actions_per_worker_map[worker_name]) + "\n"

        str_ret.strip("\n\n")
        with open(self.configuration.output_file_path, "a", encoding="utf-8") as file_handler:
            file_handler.write(str_ret)

    def init_actions_from_report_file(self, file_path):
        """
        Load the file and init actions per worker.

        :param file_path:
        :return:
        """

        with open(file_path, encoding="utf-8") as file_handler:
            str_src = file_handler.read()

        while "\n\n" in str_src:
            str_src = str_src.replace("\n\n", "\n")

        lst_per_worker = str_src.split("worker_id:")
        dict_ret = {}
        for worker_report in lst_per_worker:
            if not worker_report.strip():
                continue
            full_name, actions_new, actions_active, actions_blocked, actions_closed = self.init_actions_per_worker(
                worker_report)
            dict_ret[full_name] = {"actions_new": actions_new,
                                   "actions_active": actions_active,
                                   "actions_blocked": actions_blocked,
                                   "actions_closed": actions_closed
                                   }
        return dict_ret

    def validate_worker_report_input(self, actions_new, actions_active, actions_blocked, actions_closed):
        """
        Go over actions and validate the input

        :param actions_new:
        :param actions_active:
        :param actions_blocked:
        :param actions_closed:
        :return:
        """

        errors = []
        for action in actions_new + actions_active + actions_blocked + actions_closed:
            if action.init_errors:
                errors.append(f"Initialization Error:\n{action.src_line}:\n" + "\n".join(action.init_errors))
            if str(action.child_id) == "0":
                if not action.child_title:
                    errors.append(f"New item Title:\n {action.src_line}")
                if action.action_comment is None:
                    errors.append(f"New item Comment:\n{action.src_line}")
                if not action.action_init_time:
                    errors.append(f"New item time Estimation:\n{action.src_line}")
            if action.action_add_time is not None and action.action_comment is None:
                errors.append(f"Updating time Comment:\n{action.src_line}")

        if errors:
            print("##########VALIDATION_START################")
            for error in errors:
                print("~~~~~~~~ERROR_START~~~~~~~~~~~~~~~")
                print(error)
                print("~~~~~~~~ERROR_END~~~~~~~~~~~~~~~")
                print()
            print("##########VALIDATION_END################")
            raise ValueError("Errors occurred, see list below")

    def init_actions_per_worker(self, worker_report):
        """

        :return:
        """
        lst_worker_report = worker_report.split("\n")

        worker_full_name = lst_worker_report[0].lower()

        index_end = lst_worker_report.index("#" * 100)
        lst_worker_report = lst_worker_report[:index_end]

        new_index = lst_worker_report.index(">NEW:")
        active_index = lst_worker_report.index(">ACTIVE:")
        blocked_index = lst_worker_report.index(">BLOCKED:")
        closed_index = lst_worker_report.index(">CLOSED:")
        lines_new = lst_worker_report[new_index + 1:active_index]
        lines_active = lst_worker_report[active_index + 1:blocked_index]
        lines_blocked = lst_worker_report[blocked_index + 1:closed_index]
        lines_closed = lst_worker_report[closed_index + 1:]

        actions_new = [DailyReportAction(line_src) for line_src in lines_new]
        actions_active = [DailyReportAction(line_src) for line_src in lines_active]
        actions_blocked = [DailyReportAction(line_src) for line_src in lines_blocked]
        actions_closed = [DailyReportAction(line_src) for line_src in lines_closed]

        self.validate_worker_report_input(actions_new, actions_active, actions_blocked, actions_closed)

        self.perform_actions_replacements(actions_new, actions_active, actions_blocked, actions_closed)

        return worker_full_name, actions_new, actions_active, actions_blocked, actions_closed

    def perform_worker_report_actions(self, worker_name, input_actions, base_actions):
        """
        Split worker report to actions.

        :param base_actions:
        :param input_actions:
        :param worker_name:
        :return:
        """

        actions_new, actions_active, actions_blocked, actions_closed = input_actions["actions_new"], \
                                                                       input_actions["actions_active"], \
                                                                       input_actions["actions_blocked"], \
                                                                       input_actions["actions_closed"]

        self.perform_base_task_management_system_changes(worker_name, actions_new, actions_active, actions_blocked,
                                                         actions_closed)

        self.perform_task_management_system_status_changes(base_actions, actions_new, actions_active, actions_blocked,
                                                           actions_closed)
        str_date = datetime.datetime.now().strftime("%d/%m/%Y")
        ytb_report = self.generate_ytb_report(actions_new, actions_active, actions_blocked, actions_closed)
        named_ytb_report = f"[{str_date}] {worker_name}\n{ytb_report}"
        return named_ytb_report

    @staticmethod
    def perform_actions_replacements(actions_new, actions_active, actions_blocked, actions_closed):
        """
        Place actions according to the required action.

        :param actions_new:
        :param actions_active:
        :param actions_blocked:
        :param actions_closed:
        :return:
        """

        HumanAPI.perform_actions_replacement_per_type(actions_new, "action_new", actions_active, actions_blocked,
                                                      actions_closed)
        HumanAPI.perform_actions_replacement_per_type(actions_active, "action_activate", actions_new, actions_blocked,
                                                      actions_closed)
        HumanAPI.perform_actions_replacement_per_type(actions_blocked, "action_block", actions_new, actions_active,
                                                      actions_closed)
        HumanAPI.perform_actions_replacement_per_type(actions_closed, "action_close", actions_new, actions_active,
                                                      actions_blocked)

    @staticmethod
    def perform_actions_replacement_per_type(dst_action_list, action_name, *args):
        """
        Move action from src_lists to the dst_list according to action_name.

        :param dst_action_list:
        :param action_name:
        :param args:
        :return:
        """

        for src_action_list in args:
            to_del = []
            for action in src_action_list:
                if getattr(action, action_name):
                    dst_action_list.append(action)
                    to_del.append(action)

            for action in to_del:
                src_action_list.remove(action)

    def perform_base_task_management_system_changes(self, user_full_name, actions_new, actions_active, actions_blocked,
                                                    actions_closed):
        """
        Perform the changes using API. Create tasks if needed or add working hours.

        :param user_full_name:
        :param actions_new:
        :param actions_active:
        :param actions_blocked:
        :param actions_closed:
        :return:
        """

        parents_to_actions_map = defaultdict(list)
        for action in actions_new + actions_active + actions_blocked + actions_closed:
            if action.parent_id == "0":
                if action.parent_title in self.provisioned_new_parents_map:
                    action.parent_id = self.provisioned_new_parents_map[action.parent_title]
                else:
                    parents_to_actions_map[action.parent_title].append(action)

        for parent_title, actions in parents_to_actions_map.items():
            work_object_dict = {"type": actions[0].parent_type,
                                "title": parent_title,
                                "description": "Auto generated content. Change it manually",
                                "sprint_name": self.configuration.sprint_name,
                                "assigned_to": user_full_name
                                }
            user_story_id = self.azure_devops_api.provision_work_item_from_dict(work_object_dict)
            self.provisioned_new_parents_map[parent_title] = user_story_id

            for action in actions:
                action.parent_id = user_story_id

        for action in actions_new + actions_active + actions_blocked + actions_closed:
            if action.child_id == "0":
                work_object_dict = {"type": action.child_type,
                                    "title": action.child_title,
                                    "description": action.action_comment,
                                    "sprint_name": self.configuration.sprint_name,
                                    "assigned_to": user_full_name,
                                    "estimated_time": action.action_init_time,
                                    "parent_ids": [action.parent_id]
                                    }
                action.child_id = self.azure_devops_api.provision_work_item_from_dict(work_object_dict)

        for action in actions_new + actions_active + actions_blocked + actions_closed:
            if action.action_add_time is not None:
                self.azure_devops_api.add_hours_to_work_item(action.child_id, action.action_add_time)
            if action.action_comment is not None:
                try:
                    self.azure_devops_api.add_wit_comment(action.child_id, action.action_comment)
                except Exception as error_instance:
                    logger.info(f"Was not able to comment {action.child_id}. Error {repr(error_instance)}")

    def perform_task_management_system_status_changes(self, base_actions, actions_new, actions_active, actions_blocked,
                                                      actions_closed):
        """
        Perform all types of changes according to desired status.

        :param base_actions:
        :param actions_new:
        :param actions_active:
        :param actions_blocked:
        :param actions_closed:
        :return:
        """
        self.perform_task_management_system_status_changes_per_wit_type(WorkObject.Status.NEW, actions_new,
                                                                        base_actions["actions_new"])
        self.perform_task_management_system_status_changes_per_wit_type(WorkObject.Status.ACTIVE, actions_active,
                                                                        base_actions["actions_active"])
        self.perform_task_management_system_status_changes_per_wit_type(WorkObject.Status.BLOCKED, actions_blocked,
                                                                        base_actions["actions_blocked"])
        self.perform_task_management_system_status_changes_per_wit_type(WorkObject.Status.CLOSED, actions_closed,
                                                                        base_actions["actions_closed"])

    def perform_task_management_system_status_changes_per_wit_type(self, wit_type, desired_actions, base_actions):
        """
        Perform the change in task system according to the desired status.

        :param wit_type:
        :param desired_actions:
        :param base_actions:
        :return:
        """
        base_action_child_ids = [action.child_id for action in base_actions]

        for action in desired_actions:
            if action.child_id not in base_action_child_ids:
                self.azure_devops_api.change_wit_state(action.child_id,
                                                       WorkObject.wit_type_to_azure_devops_state(wit_type))

    @staticmethod
    def action_to_ytb_report_line(action):
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
        str_ret += "\n".join([self.action_to_ytb_report_line(action) for action in
                              sorted(actions_new + actions_active + actions_blocked + actions_closed,
                                     key=lambda x: str(x.parent_id)) if action.action_add_time])
        str_ret += "\nT:\n"
        str_ret += "\n".join(
            [self.action_to_ytb_report_line(action) for action in sorted(actions_active, key=lambda x: str(x.parent_id))
             if
             not action.action_close])

        blocked_actions = [self.action_to_ytb_report_line(action) for action in
                           sorted(actions_blocked, key=lambda x: str(x.parent_id))]
        if len(blocked_actions) == 0:
            str_ret += "\nB: None\n"
        else:
            str_ret += "\nB:\n"
            str_ret += "\n".join(blocked_actions)

        while "\n\n" in str_ret:
            str_ret = str_ret.replace("\n\n", "\n")

        str_ret += "\n"
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

        str_report += "#" * 100 + "\n"

        return str_report

    def daily_routine(self):
        """
        Make it the best way

        :param daily_hapi_file_path:
        :param protected_output_file_path:
        :param sprint_name:
        :return:
        """
        if not os.path.exists(self.configuration.protected_input_file_path):
            self.daily_report()
            return

        if not os.path.exists(self.configuration.daily_hr_output_file_path):
            self.generate_daily_hr()
            return

        self.daily_action()


    def validate_daily_input(self, file_path):
        """
        Validate the input syntax is correct.

        :param file_path:
        :return:
        """
        try:
            self.init_actions_from_report_file(file_path)
            print("Validation success!!!")
        except ValueError as inst:
            if "Errors occurred, see list below" not in repr(inst):
                raise

    def generate_work_plan(self, work_plan_file_path):
        """
        Generate list of dicts from objects.

        :param work_plan_file_path:
        :return:
        """
        items = CommonUtils.load_object_from_module(work_plan_file_path, "main")

        self.generate_auto_data(items)
        items_map = self.flattern_work_plan_tree(items)

        self.validate_work_plan(items_map)
        sprints_map = self.split_to_sprints(items_map)
        for sprint_name, sprint_items in sprints_map.items():
            summaries_map = self.generate_work_plan_summaries(sprint_items)
            file_path = self.configuration.work_plan_output_file_path_template.format(sprint_name=sprint_name.replace(" ", "_"))
            dir_path = os.path.dirname(file_path)
            os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file_handler:
                json.dump(CommonUtils.convert_to_dict(sprint_items), file_handler, indent=4)

            with open(self.configuration.work_plan_summary_output_file_path_template.format(sprint_name=sprint_name.replace(" ", "_")), "w", encoding="utf-8") as file_handler:
                summary = ("-"*40+"\n").join(summaries_map[item.hapi_uid].format_pprint(shift=4) for item in sprint_items if item.hapi_uid in summaries_map)
                file_handler.write(summary)

        return items_map

    def generate_auto_data(self, items, prefix="", sprint_name="", assigned_to=""):
        """
        Generate guids common to work planning and work executing.

        :param assigned_to:
        :param sprint_name:
        :param items:
        :param prefix:
        :return:
        """
        for item in items:
            item.hapi_uid = prefix + "/" + item.title
            if sprint_name:
                if item.sprint_name != sprint_name:
                    if item.sprint_name:
                        raise RuntimeError(f"Item '{item.title}' sprint_name was set to '{item.sprint_name}' but received explicit sprint_name: '{sprint_name}'")
                    item.sprint_name = sprint_name

            if assigned_to:
                if item.assigned_to != assigned_to:
                    if item.assigned_to:
                        raise RuntimeError(f"Item '{item.title}' assigned_to was set to '{item.assigned_to}' but received explicit assigned_to: '{assigned_to}'")
                    item.assigned_to = assigned_to

            self.generate_auto_data(item.children, prefix=item.hapi_uid, sprint_name=item.sprint_name, assigned_to=item.assigned_to)

    def flattern_work_plan_tree(self, items):
        """
        Create dictionary from work items. By hapi_uid.

        :param items:
        :return:
        """

        ret = {item.hapi_uid: item for item in items}

        for item in items:
            item.child_ids = [child.id for child in item.children if child.id is not None]
            item.child_hapi_uids = [child.hapi_uid for child in item.children if child.hapi_uid is not None]
            ret.update(self.flattern_work_plan_tree(item.children))
            item.children = []

        return ret

    @staticmethod
    def validate_work_plan(items_map: dict):
        """
        Validate user input.

        :param items_map:
        :return:
        """
        seen_values = defaultdict(list)
        errors = []
        for item in items_map.values():
            if item.child_hapi_uids:
                if item.estimated_time is not None:
                    errors.append(f"Remove estimated_time for parent with children: '{item.title}'")

                if item.type != "Feature":
                    # Parent/children sprint validation
                    child_sprint_names = {items_map[child_hapi_uid].sprint_name for child_hapi_uid in item.child_hapi_uids}
                    if len(child_sprint_names) != 1:
                        errors.append(f"Parent '{item.title}' Sprint: '{item.sprint_name}', children Sprints: '{child_sprint_names}'")
                    elif item.sprint_name != list(child_sprint_names)[0]:
                        errors.append(f"Parent '{item.title}' Sprint: '{item.sprint_name}', children's Sprint: '{list(child_sprint_names)[0]}'")

            elif item.estimated_time is None:
                errors.append(f"Item 'estimated_time' was not set: '{item.title}'")

            if len(item.title.split(" ")) > 7:
                errors.append(f"Item title number of words > 7: '{item.title}'")

            if item.id is None and item.hapi_uid is None:
                errors.append(f"Neither item id or hapi_uid were set: '{item.title}'")

            for param in ["description", "dod", "priority", "sprint_name", "assigned_to"]:
                if getattr(item, param) is None:
                    errors.append(f"Item '{param}' was not set: '{item.title}'")

            for param in ["description", "title", "dod", "hapi_uid"]:
                item_param = getattr(item, param)
                if item_param in seen_values[param]:
                    errors.append(f"Parameter '{param}' exists in multiple items with value: '{item_param}'")
                else:
                    seen_values[param].append(item_param)

        if errors:
            raise HumanAPI.ValidationError("\n".join(errors))

        for item in reversed(items_map.values()):
            if item.child_hapi_uids:
                item.estimated_time = sum(items_map[child_hapi_uid].estimated_time for child_hapi_uid in item.child_hapi_uids)

    def split_to_sprints(self, items_map):
        """
        Split items by sprint

        :param items_map:
        :return:
        """

        ret = defaultdict(list)
        for item in items_map.values():
            ret[item.sprint_name].append(item)
        return ret

    def generate_work_plan_summaries(self, items):
        """
        Generate work plan summary.

        :param items_map:
        :return:
        """

        summaries = {item.hapi_uid: item.generate_summary() for item in items}
        child_hapi_uids = []
        for item in reversed(items):
            if item.type == "Feature":
                continue

            if item.child_hapi_uids:
                child_hapi_uids += item.child_hapi_uids
                summaries[item.hapi_uid].lines += ["", "Children:"]
            summaries[item.hapi_uid].blocks = [summaries[hapi_uid] for hapi_uid in item.child_hapi_uids]

        # Return only top level summaries (Children are inside)
        return {uid: summary for uid, summary in summaries.items() if uid not in child_hapi_uids}

    class ValidationError(ValueError):
        """
        Input validation Error
        """

    def provision_work_plan(self, workplan_file_path):
        """
        Provision work_plan into the TMS
        work_object_dict = {"type": action.child_type,
                            "title": action.child_title,
                            "description": action.action_comment,
                            "sprint_name": self.configuration.sprint_name,
                            "assigned_to": user_full_name,
                            "estimated_time": action.action_init_time,
                            "parent_ids": [action.parent_id]
                            }

        :param workplan_file_path:
        :return:
        """

        self.save_sprint_work_status(self.configuration.sprint_start_status_file_path)

        with open(workplan_file_path, encoding="utf-8") as file_handler:
            ret = json.load(file_handler)

        hapi_uids_map = {}
        for work_object_dict in ret:
            tmp_dict = copy.deepcopy(work_object_dict)
            for local_var in ['hapi_uid', 'child_hapi_uids', 'dod']:
                try:
                    del tmp_dict[local_var]
                except KeyError:
                    pass

            work_object_dict["id"] = str(self.azure_devops_api.provision_work_item_from_dict(tmp_dict))
            hapi_uids_map[work_object_dict["hapi_uid"]] = work_object_dict

        with open(workplan_file_path, "w", encoding="utf-8") as file_handler:
            json.dump(ret, file_handler, indent=4)

        for work_object_dict in hapi_uids_map.values():
            status_comment = "human_api_json_encoded_current_status:"+json.dumps(work_object_dict)
            self.azure_devops_api.add_wit_comment(work_object_dict["id"], status_comment)
            children_hapi_uids = work_object_dict.get("child_hapi_uids")
            if children_hapi_uids:
                parent_id = work_object_dict["id"]
                for child_hapi_uid in children_hapi_uids:
                    child_id = hapi_uids_map[child_hapi_uid]["id"]
                    self.azure_devops_api.set_wit_parent(child_id, parent_id)

    def save_sprint_work_status(self, file_path):
        """
        Save current status to a file.

        :param file_path:
        :return:
        """

        sprints = self.get_sprints(sprint_names=[self.configuration.sprint_name])
        self.init_tasks_map(sprints=sprints)

        lst_ret = [*[obj for obj in self.tasks.values() if obj.sprint_name == self.configuration.sprint_name],
                   *[obj for obj in self.bugs.values() if obj.sprint_name == self.configuration.sprint_name]]

        seen = list(set(parent_id for obj in lst_ret for parent_id in obj.parent_ids))
        lst_ret += [obj for obj in [*self.tasks.values(), *self.tasks.values(), *self.user_stories.values()]
                    if obj.id in seen]

        seen = list(set(parent_id for obj in lst_ret for parent_id in obj.parent_ids))
        lst_ret += [obj for obj in [*self.tasks.values(), *self.tasks.values(), *self.user_stories.values(), *self.features.values()]
                    if obj.id in seen]

        seen = list(set(parent_id for obj in lst_ret for parent_id in obj.parent_ids))
        lst_ret += [obj for obj in
                    [*self.tasks.values(), *self.tasks.values(), *self.user_stories.values(), *self.features.values(), *self.epics.values()]
                    if obj.id in seen]

        lst_ret_ids = list(set(obj.id for obj in lst_ret))

        lst_ret_final = []
        for obj in lst_ret:
            if obj.id in lst_ret_ids:
                lst_ret_ids.remove(obj.id)
                lst_ret_final.append(obj.convert_to_dict())

        with open(file_path, "w", encoding="utf-8") as file_handler:
            json.dump(lst_ret_final, file_handler)

    def retrospective(self):
        """
        Retrospective

        :return:
        """

        if not os.path.exists(self.configuration.sprint_finish_status_file_path):
            self.save_sprint_work_status(self.configuration.sprint_finish_status_file_path)

        ret = self.generate_retrospective_planned_vs_current()
        return ret

    def generate_retrospective_planned_vs_current(self):
        """
        Generate retro based on planned.

        :return:
        """
        tb_ret = TextBlock("Retro")

        with open(self.configuration.work_plan_output_file_path, encoding="utf-8") as file_handler:
            sprint_planned_items_dicts = json.load(file_handler)

        sprint_planned_items = self.generate_work_objects_from_dicts(sprint_planned_items_dicts)
        sprint_plan_work_objects_map = self.split_by_worker(sprint_planned_items)

        with open(self.configuration.sprint_finish_status_file_path, encoding="utf-8") as file_handler:
            sprint_finished_items_dicts = json.load(file_handler)

        sprint_finished_items = self.generate_work_objects_from_dicts(sprint_finished_items_dicts)
        sprint_finish_work_objects_map = self.split_by_worker(sprint_finished_items)

        for worker in sprint_plan_work_objects_map:
            tb_ret_block = self.generate_retrospective_planned_vs_current_per_worker(worker, sprint_plan_work_objects_map[worker], sprint_finish_work_objects_map[worker])
            tb_ret.blocks.append(tb_ret_block)

        print(tb_ret.format_pprint(shift=2))
        return tb_ret

    @staticmethod
    def generate_retrospective_planned_vs_current_per_worker(worker, work_objects_planned, work_objects_current):
        """
        Generate retrospective.

        :param worker:
        :param work_objects_planned:
        :param work_objects_current:
        :return:
        """
        htb_ret = TextBlock(worker)
        work_objects_current_map = {obj.id: obj for obj in work_objects_current}
        work_objects_planned_map = {obj.id: obj for obj in work_objects_planned}
        for work_object_planned in work_objects_planned:
            if work_object_planned.type not in ["Task", "Bug"]:
                continue
            if work_object_planned.id in work_objects_current_map:
                current_work_object = work_objects_current_map[work_object_planned.id]
                if current_work_object.status != "CLOSED":
                    htb_ret.lines.append(f"Not closed {current_work_object.title}")
            else:
                htb_ret.lines.append(f"Removed from sprint {work_object_planned.title}")

        ad_hoc_planned = 0
        ad_hoc_reported = 0
        for work_object_current in work_objects_current:
            if work_object_current.type not in ["Task", "Bug"]:
                continue
            if work_object_current.id not in work_objects_planned_map:
                htb_ret.lines.append(f"Unplanned ad-hoc work {work_object_current.title}, {work_object_current.sprint_name}, {work_object_current.id} ")
                ad_hoc_planned += work_object_current.estimated_time
                ad_hoc_reported += work_object_current.completed_time


        return htb_ret
