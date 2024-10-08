"""
Manage Azure Devops

"""

# pylint: disable= too-many-lines
import json
import datetime
import os
from collections import defaultdict

import requests
from horey.common_utils.text_block import TextBlock
from horey.h_logger import get_logger
from horey.azure_devops_api.azure_devops_api_configuration_policy import (
    AzureDevopsAPIConfigurationPolicy,
)
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class AzureDevopsObject:
    """
    Common object.
    """

    def __init__(self, dict_src):
        self.dict_src = dict_src
        for key, value in dict_src.items():
            setattr(self, key, value)
        self._start_date = None
        self._finish_date = None
        self._created_date = None

    @classmethod
    def get_cache_file_name(cls):
        """
        Generate cache file name.

        :return:
        """

        return CommonUtils.camel_case_to_snake_case(cls.__name__) + ".json"

    def print(self):
        """
        Print the object.

        :return:
        """

        for field_name, field_value in self.dict_src.items():
            print(f"--> {field_name}: {field_value}")

    @staticmethod
    def strptime(value):
        """
        Standard Azure time string to date_time

        :param value:
        :return:

        """

        if value is None:
            return None

        if "." in value:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


class WorkItem(AzureDevopsObject):
    """
    Work item -task, user story, feature, epic etc.
    """

    def __init__(self, dict_src):
        self.fields = {}
        self.relations = []
        self.id = None

        super().__init__(dict_src)

    def print(self):
        """
        Print the fields.

        :return:
        """

        for field_name, field_value in self.fields.items():
            print(f"--> {field_name}: {field_value}")

    @property
    def parent_id(self):
        """
        Extract parent id.

        :return:
        """
        ret = []
        for relation in self.relations:
            if "name" not in relation["attributes"]:
                continue
            if relation["attributes"]["name"] == "Parent":
                ret.append(int(relation["url"].split("/")[-1]))
        if len(ret) > 1:
            raise ValueError(ret)

        return ret[0] if ret else None

    @property
    def title(self):
        """
        WI title

        :return:
        """

        if "error" in self.dict_src:
            return ""

        fields = self.dict_src.get("fields")

        if fields is None:
            raise RuntimeError(f"'fields' were not set: {self.dict_src}")

        return fields["System.Title"]

    @property
    def assigned_to(self):
        """
        User data dict

        :return:
        """

        return self.dict_src["fields"].get("System.AssignedTo")

    @property
    def iteration_path(self):
        """
        Kind of name but has multiple levels.

        :return:
        """

        try:
            return self.dict_src["fields"]["System.IterationPath"]
        except KeyError:
            return None

    @property
    def completed_work_hours(self):
        """
        Property.

        :return:
        """
        return self.fields.get("Microsoft.VSTS.Scheduling.CompletedWork")

    def get_remaining_work(self, default=None):
        """
        Get remaining hours.

        :param default:
        :return:
        """

        ret = self.dict_src["fields"].get("Microsoft.VSTS.Scheduling.RemainingWork")
        if ret is not None:
            return ret

        if default is None:
            raise RuntimeError(f"Neither RemainingWork not default were set in {self.title} work item")

        return default

    @property
    def work_item_type(self):
        """
        Azure wit Type.

        :return:
        """
        try:
            return self.dict_src["fields"]["System.WorkItemType"]
        except KeyError:
            return None

    @property
    def created_date(self):
        """
        WIT creation
        :return:
        """
        if self._created_date is None:
            if "fields" not in self.dict_src:
                return None

            value = self.dict_src["fields"]["System.CreatedDate"]
            self._created_date = self.strptime(value)

        return self._created_date

    @property
    def resolved_date(self):
        """
        None if doesn't exist
        :return:
        """
        value = self.fields.get("Microsoft.VSTS.Common.ResolvedDate")
        return self.strptime(value)

    @property
    def closed_date(self):
        """
        None if doesn't exist
        :return:
        """
        value = self.fields.get("Microsoft.VSTS.Common.ClosedDate")
        return self.strptime(value)

    @property
    def state_change_date_date(self):
        """
        Last state
        :return:
        """
        value = self.fields.get("Microsoft.VSTS.Common.StateChangeDate")
        return self.strptime(value)

    @property
    def finish_date(self):
        """
        Removed/Resolved/Closed
        :return:
        """
        if self.resolved_date is not None:
            return self.resolved_date

        if self.closed_date is not None:
            return self.closed_date

        if self.state == "Removed":
            if self.state_change_date_date is not None:
                return self.state_change_date_date

        if self.state == "Merge Request":
            return None

        raise ValueError(f"Unknown state: {self.state}")

    @property
    def state(self):
        """
        Current
        :return:
        """
        return self.fields.get("System.State")

    @property
    def activated_date(self):
        """
        Automatic. None if doesn't exist

        :return:
        """
        value = self.fields.get("Microsoft.VSTS.Common.ActivatedDate")
        return self.strptime(value)

    @property
    def original_estimate(self):
        """
        Reported
        :return:
        """
        value = self.fields.get("Microsoft.VSTS.Scheduling.OriginalEstimate")
        return value

    # pylint: disable= too-many-branches
    def convert_to_dict(self):
        """
        Init base attributes.

        :return:
        """

        try:
            ret = {
               "id": str(self.fields["System.Id"]),
               "title": self.fields["System.Title"],
               "created_by": self.fields["System.CreatedBy"]["displayName"],
               "status": self.convert_to_dict_status(),
               "created_date": CommonUtils.convert_to_dict(self.strptime(self.fields["System.CreatedDate"])),
               "child_ids": [],
               "parent_ids": [],
               "sprint_name": self.fields.get("System.IterationLevel2") or self.fields["System.IterationLevel1"],
               "estimated_time": self.original_estimate,
               "completed_time": self.completed_work_hours
               }
        except Exception:
            if "you do not have permissions to read" in str(self.dict_src):
                return self.dict_src
            raise

        try:
            ret["type"] = self.fields["System.WorkItemType"].replace(" ", "")
        except Exception as inst_error:
            logger.info(f"Error: {inst_error}")

        if self.fields.get("System.AssignedTo") is not None:
            ret["assigned_to"] = self.fields["System.AssignedTo"]["displayName"]

        if ret["status"] == "CLOSED":
            ret["closed_date"] = self.convert_to_dict_closed_date()

        related = []
        for relation in self.relations:
            if relation["rel"] in ["ArtifactLink", "AttachedFile", "Hyperlink",
                                   "Microsoft.VSTS.TestCase.SharedParameterReferencedBy-Forward"]:
                related.append(relation)
            elif relation["attributes"]["name"] == "Child":
                ret["child_ids"].append(str(int(relation["url"].split("/")[-1])))
            elif relation["attributes"]["name"] == "Parent":
                ret["parent_ids"].append(str(int(relation["url"].split("/")[-1])))
            elif relation["attributes"]["name"] in ["Related", "Duplicate Of", "Duplicate", "Successor", "Predecessor"]:
                related.append(relation)
            else:
                raise ValueError(f"Unknown relation name in: '{relation}': '{relation['attributes']['name']}'")
        if related:
            logger.info(f"Unhandled related: {related}")

        if ret["type"] not in ["Task", "Bug", "UserStory", "Feature", "Epic", "Issue"]:
            raise ValueError(ret["type"])

        return ret

    def convert_to_dict_status(self):
        """
        Convert to standard status

        :return:
        """

        value = self.fields["System.State"]
        if value in ["New", "Active"]:
            return value.upper()

        if value in ["On Hold", "Pending Deployment", "PM Review", "Merge Request", "In Testing"]:
            return "BLOCKED"

        if value in ["Resolved", "Closed", "Removed"]:
            return "CLOSED"

        raise ValueError(f"Status unknown: {value}")

    def convert_to_dict_closed_date(self):
        """
        Find the closing date.

        :return:
        """

        value = self.fields.get("Microsoft.VSTS.Common.ClosedDate") or \
                self.fields.get("Microsoft.VSTS.Common.ResolvedDate") or \
                self.fields.get("Microsoft.VSTS.Common.StateChangeDate")
        return CommonUtils.convert_to_dict(self.strptime(value))


class Iteration(AzureDevopsObject):
    """
    Single iteration

    """

    VACATIONS = {"2023-04-25": 3,
                 "2023-04-26": 6}

    @property
    def start_date(self):
        """

        Start date.
        :return:
        """

        if self._start_date is None:
            self._start_date = datetime.datetime.strptime(self.dict_src["attributes"]["startDate"],
                                                          "%Y-%m-%dT%H:%M:%SZ")
        return self._start_date

    @property
    def finish_date(self):
        """
        End date.

        :return:
        """

        if self._finish_date is None:
            self._finish_date = datetime.datetime.strptime(self.dict_src["attributes"]["finishDate"],
                                                           "%Y-%m-%dT%H:%M:%SZ")
        return self._finish_date

    def get_hours(self, only_remaining=True):
        """
        Get hours of the spirnt.

        :param only_remaining:
        :return:
        """

        now = datetime.datetime.now()
        hours = 0
        actual_start_date = self.start_date
        if only_remaining:
            if self.finish_date < now:
                return 0
            if self.start_date < now < self.finish_date:
                hours = max(min(17 - datetime.datetime.now().hour, 6), 0)
                actual_start_date = datetime.datetime(year=now.year, month=now.month, day=now.day) + datetime.timedelta(
                    days=1)

        daygenerator = (actual_start_date + datetime.timedelta(days=x) for x in
                        range((self.finish_date - actual_start_date).days))
        days = sum(1 for day in daygenerator if day.weekday() in [0, 1, 2, 3, 6])
        for str_date, off_hours in self.VACATIONS.items():
            if actual_start_date < datetime.datetime.strptime(str_date, "%Y-%m-%d") < self.finish_date:
                hours -= off_hours

        return hours + days * 6


class Backlog(AzureDevopsObject):
    """
    Standard.
    """


class TeamMember(AzureDevopsObject):
    """
    Standard.
    """


# pylint: disable= too-many-instance-attributes
class AzureDevopsAPI:
    """
    Main class
    """

    def __init__(self, configuration: AzureDevopsAPIConfigurationPolicy = None):
        self.base_address = configuration.server_address
        self.version = "7.1"
        self.session = requests.Session()

        self.session.auth = (configuration.user, configuration.password)
        self.project_name = configuration.project_name
        self.org_name = configuration.org_name
        self.team_name = configuration.team_name
        self.configuration = configuration
        self.work_items = []
        self.nit_ = []
        self.iterations = []
        self.backlogs = []
        self.processes = []
        self.team_members = []

    def get_iterations(self, date_find=None, from_cache=False, iteration_pathes=None):
        """
        Get current by default or find by date specified.

        :param from_cache:
        :param iteration_pathes:
        :param date_find:
        :return:
        """
        if not self.iterations:
            self.init_iterations(from_cache=from_cache)

        if date_find is None and iteration_pathes is None:
            date_find = datetime.datetime.now()

        lst_ret = []
        for iteration in self.iterations:
            if date_find is not None:
                if iteration.start_date <= date_find <= iteration.finish_date:
                    lst_ret.append(iteration)
            else:
                if iteration.name in iteration_pathes:
                    lst_ret.append(iteration)

        if lst_ret:
            return lst_ret

        raise RuntimeError(f"Can not find iterations by {date_find} and {iteration_pathes}")

    def get_iteration(self, date_find=None, from_cache=False):
        """
        Get current by default or find by date specified.

        :param date_find:
        :return:
        """

        if not self.iterations:
            self.init_iterations(from_cache=from_cache)

        if date_find is None:
            date_find = datetime.datetime.now()
        for iteration in self.iterations:
            if iteration.start_date <= date_find <= iteration.finish_date:
                return iteration
        raise RuntimeError("Can not find current iteration.")

    def init_iterations(self, from_cache=False):
        """
        Fetch from API

        :return:
        """

        if from_cache:
            return self.init_items_from_cache("iterations", Iteration)

        lst_ret = []

        response = self.session.get(
            f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/teamsettings/iterations?api-version=7.0")
        if response.status_code != 200:
            raise ValueError(f"{response.status_code=}")
        ret = response.json()
        logger.info("Start fetching iterations")
        for iteration in ret["value"]:
            response = self.session.get(
                f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/teamsettings/iterations/{iteration['id']}?api-version=7.0")
            dict_src = response.json()
            lst_ret.append(Iteration(dict_src))

        self.iterations = lst_ret
        self.cache(self.iterations)
        logger.info(f"Inited {len(lst_ret)} iterations")
        return lst_ret

    def init_dashboards(self):
        """
        Fetch from API

        :return:
        """

        lst_ret = []
        response = self.session.get(
            f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/dashboard/dashboards?api-version=7.0-preview.3")
        ret = response.json()
        for dashboard in ret["value"]:
            response = self.session.get(
                f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/dashboard/dashboards/{dashboard['id']}?api-version=7.0-preview.3")
            ret = response.json()
            lst_ret.append(ret)
        return lst_ret

    def init_boards(self):
        """
        Fetch from API

        :return:
        """

        lst_ret = []
        response = self.session.get(
            f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/boards?api-version=7.0")
        ret = response.json()
        for board in ret["value"]:
            response = self.session.get(
                f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/boards/{board['id']}?api-version=7.0")
            ret = response.json()
            lst_ret.append(ret)
        return lst_ret

    def init_processes(self):
        """
        Fetch from API

        :return:
        """

        lst_ret = []
        response = self.session.get(f"https://dev.azure.com/{self.org_name}/_apis/process/processes?api-version=7.0")
        ret = response.json()
        for process in ret["value"]:
            response = self.session.get(
                f"https://dev.azure.com/{self.org_name}/_apis/process/processes/{process['id']}?api-version=7.0")
            ret = response.json()
            lst_ret.append(ret)
        self.processes = lst_ret
        return lst_ret

    def init_backlogs(self, from_cache=False):
        """
        Fetch from API

        :return:
        """

        if from_cache:
            return self.init_items_from_cache("backlogs", Backlog)

        project = self.project_name
        organization = self.org_name
        response = self.session.get(
            f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/backlogs?api-version=7.0")
        ret = response.json()
        lst_src = ret["value"]

        lst_ret = []
        logger.info("Start fetching backlogs")
        for backlog in lst_src:
            str_id = backlog["id"]
            response = self.session.get(
                f"https://dev.azure.com/{organization}/{project}/{self.team_name}/_apis/work/backlogs/{str_id}?api-version=7.0")
            dict_src = response.json()
            lst_ret.append(Backlog(dict_src))
        logger.info(f"Inited {len(lst_ret)} backlogs")

        self.backlogs = lst_ret
        self.cache(self.backlogs)
        return self.backlogs

    def init_items_from_cache(self, attribute_name, item_class):
        """
        Standard.

        :param attribute_name:
        :param item_class:
        :return:
        """
        with open(os.path.join(self.configuration.cache_dir_full_path, item_class.get_cache_file_name()),
                  encoding="utf-8") as file_handler:
            lst_src = json.load(file_handler)
        lst_ret = [item_class(dict_src) for dict_src in lst_src]

        setattr(self, attribute_name, lst_ret)

    def init_work_items(self, from_cache=False):
        """
        Fetch from API

        :return:
        """
        if from_cache:
            return self.init_items_from_cache("work_items", WorkItem)

        lst_items = self.init_work_items_by_iterations()

        self.work_items = lst_items + self.init_work_items_by_backlog(ignore_items=lst_items)

        self.cache(self.work_items)

        return self.work_items

    def init_work_items_by_iterations(self, iteration_names=None):
        """
        Init live data.

        :param iteration_names:
        :return:
        """

        lst_all = []
        lst_all_ids = []
        if not self.iterations:
            self.init_iterations()

        if iteration_names:
            iterations = [iteration for iteration in self.iterations if iteration.name in iteration_names]
        else:
            self.init_iterations()
            iterations = self.iterations
        project = self.project_name
        organization = self.org_name
        for iteration_id in [iteration.id for iteration in iterations]:
            response = self.session.get(
                f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/teamsettings/iterations/{iteration_id}/workitems?api-version=7.0")
            ret = response.json()
            lst_src = ret["workItemRelations"]

            logger.info("Fetching work items")
            for work_item_rel in lst_src:
                try:
                    int_id = work_item_rel["source"].get("id")
                except AttributeError:
                    int_id = None

                if int_id and int_id not in lst_all_ids:
                    response = self.session.get(
                        f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{int_id}?$expand=all&api-version=7.0")
                    dict_src = response.json()
                    lst_all.append(WorkItem(dict_src))
                    lst_all_ids.append(int_id)

                try:
                    int_id = work_item_rel["target"].get("id")
                except AttributeError:
                    int_id = None

                if int_id and int_id not in lst_all_ids:
                    response = self.session.get(
                        f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{int_id}?$expand=all&api-version=7.0")
                    dict_src = response.json()
                    lst_all.append(WorkItem(dict_src))
                    lst_all_ids.append(int_id)

            logger.info(f"Totally initialized {len(lst_all_ids)} until iteration: {iteration_id}")

        return self.recursive_init_work_items(lst_all)

    def recursive_init_work_items(self, lst_all, forward_only=False):
        """
        Init recursively according to relations.

        :param forward_only:
        :param lst_all:
        :return:
        """
        lst_ret = lst_all[::]
        new_items = [None]
        while new_items:
            lst_all_ids = [work_item.id for work_item in lst_ret]
            new_items = []
            for work_item in lst_ret:
                for relation in work_item.relations:
                    if forward_only:
                        hierarchy_types = ["System.LinkTypes.Hierarchy-Forward"]
                    else:
                        hierarchy_types = ["System.LinkTypes.Hierarchy-Reverse",
                                           "System.LinkTypes.Hierarchy-Forward"]

                    if relation["rel"] not in hierarchy_types:
                        continue
                    work_item_id = relation["url"].split("/")[-1]
                    if int(work_item_id) in lst_all_ids:
                        continue
                    work_item_new = self.get_work_item(work_item_id)
                    new_items.append(work_item_new)

                    lst_all_ids.append(work_item_new.id)
            logger.info(f"Recursively found another {len(new_items)} work items")
            lst_ret += new_items

        return lst_ret

    def get_work_item(self, work_item_id):
        """
        Fetch single work item
        :param work_item_id:
        :return:
        """

        response = self.session.get(
            f"https://dev.azure.com/{self.org_name}/{self.project_name}/_apis/wit/workitems/{work_item_id}?$expand=all&api-version=7.0")

        if response.status_code == 404:
            dict_src = {"id": int(work_item_id), "error": response.json()}
        elif response.status_code == 401:
            dict_src = {"id": int(work_item_id), "error": {"status_code": response.status_code, "headers": response.headers}}
        else:
            dict_src = response.json()

        return WorkItem(dict_src)

    def init_work_items_by_backlog(self, ignore_items=None):
        """
        Fetch from API

        :return:
        """
        lst_all = []
        if ignore_items is None:
            ignore_ids = []
        else:
            ignore_ids = [item.id for item in ignore_items]

        if not self.backlogs:
            self.init_backlogs()

        project = self.project_name
        organization = self.org_name
        for backlog_id in [backlog.id for backlog in self.backlogs]:
            response = self.session.get(
                f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/backlogs/{backlog_id}/workItems?api-version=7.0")
            ret = response.json()
            lst_src = ret["workItems"]

            lst_ret = []
            logger.info(f"Fetching work items for backlog: {backlog_id}")
            for work_item in lst_src:
                str_id = work_item["target"]["id"]
                if ignore_ids and (int(str_id) in ignore_ids):
                    continue
                response = self.session.get(
                    f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{str_id}?$expand=all&api-version=7.0")
                dict_src = response.json()
                lst_ret.append(WorkItem(dict_src))
            logger.info(f"Inited {len(lst_ret)} work items with backlog_id: {backlog_id}")
            lst_all += lst_ret

        return self.recursive_init_work_items(lst_all)

    def cache(self, objects):
        """
        Cache objects with dict_src

        :param objects:
        :return:
        """

        file_path = os.path.join(self.configuration.cache_dir_full_path, objects[0].get_cache_file_name())

        lst_ret = [obj.dict_src for obj in objects]
        with open(file_path, "w", encoding="utf-8") as file_handler:
            json.dump(lst_ret, file_handler)

    def init_team_members(self, from_cache=False):
        """
        Fetch from API
        https://learn.microsoft.com/en-us/rest/api/azure/devops/core/teams/get-team-members-with-extended-properties?view=azure-devops-rest-5.0&tabs=HTTP

        :return:
        """
        if from_cache:
            self.init_items_from_cache("team_members", TeamMember)
        response = self.session.get(
            f"https://dev.azure.com/{self.org_name}/_apis/projects/{self.project_name}/teams/{self.team_name}/members?api-version=7.0")
        ret = response.json()
        logger.info("Start fetching team member")
        self.team_members = [TeamMember(dict_src) for dict_src in ret["value"]]
        self.cache(self.team_members)

    def generate_clean_report(self):
        """
        Different cleanups.

        :return:
        """

        h_tb = TextBlock("Cleanup report")
        if not self.work_items:
            self.init_work_items()
        current_iteration = self.get_iteration()
        now = datetime.datetime.now()
        future_iterations_paths = [iteration.path for iteration in self.iterations if iteration.start_date > now]
        past_iterations_paths = [iteration.path for iteration in self.iterations if iteration.finish_date < now]

        current_iteration_work_items = []
        past_iterations_work_items = []
        future_iterations_work_items = []

        backlogs = defaultdict(list)

        for work_item in self.work_items:
            if work_item.iteration_path == current_iteration.path:
                current_iteration_work_items.append(work_item)
            elif work_item.iteration_path in past_iterations_paths:
                past_iterations_work_items.append(work_item)
            elif work_item.iteration_path in future_iterations_paths:
                future_iterations_work_items.append(work_item)
            else:
                backlogs[work_item.iteration_path].append(work_item.iteration_path)

        tb_ret = self.generate_clean_report_current_iteration(current_iteration_work_items)
        h_tb.blocks.append(tb_ret)

        tb_ret = self.generate_clean_report_two_iterations(current_iteration_work_items, future_iterations_work_items)
        h_tb.blocks.append(tb_ret)

        return h_tb

    def get_iteration_work_items(self, iteration):
        """
        Get iteration work items.

        :param iteration:
        :return:
        """

        return [work_item for work_item in self.work_items if work_item.iteration_path == iteration.path]

    def generate_clean_report_two_iterations(self, current_iteration_work_items, future_iterations_work_items):
        """
        Don't put off till tomorrow what you can do today.

        :param current_iteration_work_items:
        :param future_iterations_work_items:
        :return:
        """

        current_iteration = self.get_iteration()
        next_iteration = self.get_iteration(date_find=datetime.datetime.now() + datetime.timedelta(weeks=2))

        h_tb = TextBlock(f"Current ({current_iteration.path}) and following ({next_iteration.path}) sprints cleanup")

        next_iteration_work_items = [work_item for work_item in future_iterations_work_items if
                                     work_item.iteration_path == next_iteration.path]
        current_iteration_hours = current_iteration.get_hours()
        next_iteration_hours = next_iteration.get_hours()
        total_hours = current_iteration_hours + next_iteration_hours
        work_items_by_worker = self.split_work_items_by_worker(current_iteration_work_items + next_iteration_work_items)

        for worker_name, work_items in work_items_by_worker.items():
            total_remaining_hours = sum(work_item.get_remaining_work(default=3.0) for work_item in work_items)
            if total_hours < total_remaining_hours:
                h_tb.lines.append(
                    f"Worker {worker_name} has {total_remaining_hours} remaining tasks' hours but only {total_hours} working hours left")

        return h_tb

    def generate_clean_report_current_iteration(self, current_iteration_work_items):
        """
        Current iteration.

        :return:
        """

        current_iteration = self.get_iteration()
        h_tb = TextBlock(f"Current ({current_iteration.path}) sprint cleanup")

        current_iteration_hours = current_iteration.get_hours()
        total_hours = current_iteration_hours
        work_items_by_worker = self.split_work_items_by_worker(current_iteration_work_items)

        for worker_name, work_items in work_items_by_worker.items():
            total_remaining_hours = sum(work_item.get_remaining_work(default=3.0) for work_item in work_items)
            if total_hours < total_remaining_hours:
                h_tb.lines.append(
                    f"Worker {worker_name} has {total_remaining_hours} remaining tasks' hours but only {total_hours} working hours left")

        return h_tb

    @staticmethod
    def split_work_items_by_worker(work_items):
        """
        Split by worker display name.

        :param work_items:
        :return:
        """

        ret_dict = defaultdict(list)
        for work_item in work_items:
            ret_dict[work_item.assigned_to["displayName"]].append(work_item)
        return ret_dict

    def post(self, url, data):
        """
        Perform post request.

        :param request_path:
        :param data:
        :return:
        """
        response = self.session.post(url, data=json.dumps(data))
        if response.status_code != 200:
            raise RuntimeError(
                f"Request to azuredevops api api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def patch(self, url, data):
        """
        Send patch request

        :param url:
        :param data:
        :return:
        """

        self.session.headers.update(
            {
                "Content-Type": "application/json-patch+json",
                "User-Agent": "python/horey",
                "Cache-Control": "no-cache",
            })
        response = self.session.patch(url, data=json.dumps(data))

        if response.status_code != 200:
            logger.error(response)
            raise RuntimeError(response.text)

        return response.json()

    def add_hours_to_work_item(self, wit_id, float_hours):
        """
        Add int hours to the work item.

        :param wit_id:
        :param float_hours:
        :return:
        """
        work_item = self.get_work_item(wit_id)

        logger.info(f"WIT:{wit_id} adding '{float_hours}' hours to the effort time")
        completed_work_hours = 0 if work_item.completed_work_hours is None else work_item.completed_work_hours
        request_data = \
            [{
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.CompletedWork",
                "value": str(completed_work_hours + float_hours)
            }]
        url = f"https://dev.azure.com/{self.org_name}/_apis/wit/workitems/{wit_id}?api-version=7.0"
        return self.patch(url, request_data)

    def change_iteration(self, wit_id, iteration_name):
        """
        Add int hours to the work item.

        :param wit_id:
        :param iteration_name:
        :return:
        """
        logger.info(f"WIT:{wit_id} changing iteration to '{iteration_name}'")
        request_data = \
            [{
                "op": "add",
                "path": "/fields/System.IterationPath",
                "value": iteration_name
            }]
        url = f"https://dev.azure.com/{self.org_name}/_apis/wit/workitems/{wit_id}?api-version=7.0"

        return self.patch(url, request_data)

    def set_wit_parent(self, wit_id, parent_id):
        """

        :param wit_id:
        :param parent_id:
        :return:
        """
        logger.info(f"WIT:{wit_id} setting new parent to '{parent_id}'")
        request_data = [{
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": f"https://dev.azure.com/{self.org_name}/{self.project_name}/apis/wit/workItems/{parent_id}"
            }
        }]

        url = f"https://dev.azure.com/{self.org_name}/_apis/wit/workitems/{wit_id}?api-version=7.0"
        try:
            return self.patch(url, request_data)
        except Exception as error_inst:
            if "only one Parent link" not in repr(error_inst):
                raise
            logger.info(f"Removing parent: {wit_id}")
            request_remove_parent = [{"op": "remove", "path": "/relations/0"}]
            self.patch(url, request_remove_parent)

            logger.info(f"Adding parent: {wit_id}")
            return self.patch(url, request_data)

    def set_work_object_child(self, wit_id, child_id):
        """

        :param wit_id:
        :param child_id:
        :return:
        """
        logger.info(f"WIT:{wit_id} setting new parent to '{child_id}'")
        request_data = [{
            "op": "add",
            "path": "/relations/-",
            "value": {

                "rel": "System.LinkTypes.Hierarchy-Forward",
                "url": f"https://dev.azure.com/{self.org_name}/{self.project_name}/apis/wit/workItems/{child_id}"
            }
        }]

        url = f"https://dev.azure.com/{self.org_name}/_apis/wit/workitems/{wit_id}?api-version=7.0"
        return self.patch(url, request_data)

    def change_wit_state(self, wit_id, state):
        """
        Change work item state.

        :param wit_id:
        :param state:
        :return:
        """

        logger.info(f"WIT:{wit_id} setting new state to '{state}'")
        request_data = \
            [{
                "op": "add",
                "path": "/fields/System.State",
                "value": state
            }]
        url = f"https://dev.azure.com/{self.org_name}/_apis/wit/workitems/{wit_id}?api-version=7.0"

        return self.patch(url, request_data)

    def add_wit_comment(self, wit_id, comment):
        """
        Add a comment.
        https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/comments/add?view=azure-devops-rest-7.0&tabs=HTTP

        :param wit_id:
        :param comment:
        :return:
        """
        logger.info(f"WIT:{wit_id} adding comment '{comment}'")
        request_data = \
            {
                "text": comment
            }

        url = f"https://dev.azure.com/{self.org_name}/{self.project_name}/_apis/wit/workitems/{wit_id}/comments?api-version=7.0-preview.3"
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "python/horey",
            })
        return self.post(url, request_data)

    # pylint:disable= too-many-arguments
    def provision_work_item_by_params(self, wit_type, wit_title, wit_description, iteration_partial_path=None,
                                      original_estimate_time=None, assigned_to=None, parent_id=None):
        """
        Provision work item by parameters received.
        https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/create?view=azure-devops-rest-7.0&tabs=HTTP

        :param parent_id:
        :param wit_description:
        :param assigned_to:
        :param original_estimate_time:
        :param iteration_partial_path:
        :param wit_type:
        :param wit_title:
        :return:
        """
        if wit_type == "user_story":
            wit_url_type = "$User%20Story"
        elif wit_type == "task":
            wit_url_type = "$Task"
        elif wit_type == "bug":
            wit_url_type = "$Bug"
        else:
            raise RuntimeError(f"wit_type {wit_type} != user_story")

        logger.info(f"Creating new WIT: {wit_type}: '{wit_title}'")
        # suppressNotifications=true&
        url = f"https://dev.azure.com/{self.org_name}/{self.project_name}/_apis/wit/workitems/{wit_url_type}?api-version=7.0"
        request_data = \
            [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": wit_title
                },
                {
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": wit_description
                },
                {
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.Priority",
                    "value": "2"
                }
            ]

        if original_estimate_time is not None:
            request_data.append(
                {
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Scheduling.OriginalEstimate",
                    "value": original_estimate_time
                })
        logger.info(f"Creating Work Item with parameters: {request_data}")

        if assigned_to is not None:
            request_data.append({"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to})

        self.session.headers.update(
            {
                "Content-Type": "application/json-patch+json",
                "User-Agent": "python/horey",
            })
        ret = self.post(url, request_data)
        wit_id = ret.get("id")
        logger.info(f"WIT:{wit_id} created. Type: '{wit_type}' Title '{wit_title}'")
        if iteration_partial_path is not None:
            self.change_iteration(wit_id, f"{self.project_name}\\\\{iteration_partial_path}")

        if parent_id is not None:
            self.set_wit_parent(wit_id, parent_id)

        return wit_id

    # pylint: disable= too-many-branches, too-many-statements, too-many-locals
    def provision_work_item_from_dict(self, dict_src):
        """
        Provision work item by parameters received.
        https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/create?view=azure-devops-rest-7.0&tabs=HTTP

        :param dict_src:

        :return:
        """
        if "id" in dict_src:
            return self.update_work_item_from_dict(dict_src)

        left_attributes = list(dict_src.keys())
        wit_type = dict_src["type"]
        left_attributes.remove("type")
        if wit_type == "UserStory":
            wit_url_type = "$User%20Story"
        elif wit_type == "Task":
            wit_url_type = "$Task"
        elif wit_type == "Bug":
            wit_url_type = "$Bug"
        else:
            raise RuntimeError(f"wit_type {wit_type} != user_story")

        wit_title = dict_src["title"]
        left_attributes.remove("title")
        logger.info(f"Creating new WIT: {wit_type}: '{wit_title}'")
        # suppressNotifications=true&
        url = f"https://dev.azure.com/{self.org_name}/{self.project_name}/_apis/wit/workitems/{wit_url_type}?api-version=7.0"
        wit_description = dict_src["description"]
        left_attributes.remove("description")
        request_data = \
            [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": wit_title
                },
                {
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": wit_description
                }
            ]

        if "priority" in left_attributes:
            priority = dict_src["priority"]
            left_attributes.remove("priority")
        else:
            priority = "2"

        request_data.append({
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Priority",
            "value": priority
        })

        if "sprint_name" in left_attributes:
            request_data.append({
                    "op": "add",
                    "path": "/fields/System.IterationPath",
                    "value": f"{self.project_name}\\\\{dict_src['sprint_name']}"
                })
            left_attributes.remove("sprint_name")

        if "estimated_time" in dict_src:
            original_estimate_time = dict_src["estimated_time"]
            left_attributes.remove("estimated_time")
            if original_estimate_time is not None:
                request_data.append(
                    {
                        "op": "add",
                        "path": "/fields/Microsoft.VSTS.Scheduling.OriginalEstimate",
                        "value": original_estimate_time
                    })
                request_data.append(
                    {
                        "op": "add",
                        "path": "/fields/Microsoft.VSTS.Scheduling.RemainingWork",
                        "value": original_estimate_time
                    })

        logger.info(f"Creating Work Item with parameters: {request_data}")

        assigned_to = dict_src["assigned_to"]
        left_attributes.remove("assigned_to")
        if assigned_to is not None:
            request_data.append({"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to})

        if "completed_time" in dict_src:
            completed_time = dict_src["completed_time"]
            left_attributes.remove("completed_time")
            request_data.append({
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.CompletedWork",
                "value": completed_time
            })

        self.session.headers.update(
            {
                "Content-Type": "application/json-patch+json",
                "User-Agent": "python/horey",
            })
        ret = self.post(url, request_data)
        wit_id = ret.get("id")
        logger.info(f"WIT:{wit_id} created. Type: '{wit_type}' Title '{wit_title}'")

        if "parent_ids" in left_attributes:
            parent_id = dict_src["parent_ids"][0]
            if parent_id is not None:
                self.set_wit_parent(wit_id, parent_id)
            left_attributes.remove("parent_ids")

        if "child_ids" in left_attributes:
            for child_id in dict_src["child_ids"]:
                self.set_wit_parent(child_id, wit_id)
            left_attributes.remove("child_ids")

        if left_attributes:
            raise ValueError(left_attributes)

        return wit_id

    def update_work_item_from_dict(self, dict_src):
        """
        Update existing item.

        :return:
        """
        request_data = []
        wit_id = dict_src.pop("id")
        logger.info(f"WIT:{wit_id} changing params '{dict_src}'")

        if "sprint_name" in dict_src:
            request_data.append({
                "op": "add",
                "path": "/fields/System.IterationPath",
                "value": f"{self.project_name}\\\\{dict_src.pop('sprint_name')}"
            })

        if "completed_time" in dict_src:
            request_data.append({
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.CompletedWork",
                "value": str(dict_src.pop("completed_time"))
            })

        if "estimated_time" in dict_src:
            request_data.append({
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.OriginalEstimate",
                "value": str(dict_src.pop("estimated_time"))
            })

        if dict_src:
            raise ValueError(dict_src)

        url = f"https://dev.azure.com/{self.org_name}/_apis/wit/workitems/{wit_id}?api-version=7.0"

        self.patch(url, request_data)
        return wit_id

    def generate_retrospective_times(self, search_strings, ignore_wobject_ids=None):
        """
        Search for work items with these strings inside

        :param ignore_wobject_ids:
        :param search_strings:
        :return:
        """
        wits_match = []
        htb_all_wips = TextBlock("Found wips")
        for wit in self.work_items:
            if ignore_wobject_ids and (wit.id in ignore_wobject_ids or wit.parent_id in ignore_wobject_ids):
                continue

            for search_string in [search_string.lower().strip() for search_string in search_strings]:
                if search_string in wit.title.lower():
                    wits_match.append(wit)
                    htb_all_wips.lines.append(f"{wit.work_item_type}, {wit.id}, {wit.title}")
                    break

        recursively_found = self.recursive_init_work_items(wits_match, forward_only=True)
        recursively_found = sorted(recursively_found, key=lambda _wit: _wit.strptime(_wit.fields["Microsoft.VSTS.Common.StateChangeDate"]))
        for wit in recursively_found:
            print(f'{wit.strptime(wit.fields["Microsoft.VSTS.Common.StateChangeDate"]).strftime("%d.%m.%Y")} {wit.title}')
            #wit.activated_date.strftime("%d.%m.%Y")

    def generate_solution_retrospective(self, search_strings, ignore_wobject_ids=None):
        """
        Search for work items with these strings inside

        :param ignore_wobject_ids:
        :param search_strings:
        :return:
        """
        wits_match = []
        htb_all_wips = TextBlock("Found wips")
        for wit in self.work_items:
            if ignore_wobject_ids and (wit.id in ignore_wobject_ids or wit.parent_id in ignore_wobject_ids):
                continue

            for search_string in [search_string.lower().strip() for search_string in search_strings]:
                if search_string in wit.title.lower():
                    wits_match.append(wit)
                    htb_all_wips.lines.append(f"{wit.work_item_type}, {wit.id}, {wit.title}")
                    break

        recursively_found = self.recursive_init_work_items(wits_match, forward_only=True)
        if ignore_wobject_ids:
            recursively_found = [x for x in recursively_found if x.id not in ignore_wobject_ids and x.parent_id not in ignore_wobject_ids]

        base_task_bags = [wit for wit in wits_match if wit.work_item_type in ["Task", "Bug"]]
        recursive_task_bags = [wit for wit in recursively_found if wit.work_item_type in ["Task", "Bug"]]
        logger.info(f"Found {len(base_task_bags)} from string and {len(recursive_task_bags)} recursively")

        htb_ret = TextBlock("Retrospective")
        htb_ret.blocks.append(htb_all_wips)
        htb_low = self.generate_retrospective_per_type(
            [wit for wit in recursively_found if wit.work_item_type in ["Task", "Bug"]])
        htb_low.header = "Tasks/Bugs"
        htb_ret.blocks.append(htb_low)

        high_order_wits = [wit for wit in recursively_found if wit.work_item_type not in ["Task", "Bug", None]]
        htb_high = self.generate_retrospective_per_type(high_order_wits)
        htb_high.header = "/".join({wit.work_item_type for wit in high_order_wits})
        htb_ret.blocks.append(htb_high)
        print(htb_ret)
        return htb_ret

    def generate_retrospective_per_type(self, wits):
        """

        :param wits:
        :return:
        """

        htb_ret = TextBlock("")
        types = []

        wits = [wit for wit in wits if wit.created_date is not None]

        for wit in sorted(wits, key=lambda wit: wit.created_date):
            completed_work_hours = str(wit.completed_work_hours) if wit.completed_work_hours is not None else "?"
            activated_date = wit.activated_date.strftime("%d.%m.%Y") if wit.activated_date is not None else "?"
            original_estimate = str(wit.original_estimate) if wit.original_estimate is not None else "?"
            if wit.state in ["New", "Active", "On Hold", "Pending Deployment", "PM Review"]:
                finish_date = "WIP"
            else:
                finish_date = wit.finish_date.strftime("%d.%m.%Y") if wit.finish_date is not None else "?"

            created_date = wit.created_date.strftime("%d.%m.%Y")
            if "." in finish_date and created_date.split(".")[-1] == finish_date.split(".")[-1]:
                created_date = created_date[:created_date.rfind(".")]
                activated_date = activated_date[
                                 :activated_date.rfind(".")] if "." in activated_date else activated_date
                finish_date = finish_date[:finish_date.rfind(".")]

            str_line = f'{created_date}->{activated_date}->{finish_date} [{wit.fields["System.CreatedBy"]["displayName"]}] <{original_estimate}/{completed_work_hours}> Title: {wit.title.strip().capitalize()}'
            htb_ret.lines.append(str_line)
            if wit.work_item_type not in types:
                types.append(wit.work_item_type)
        return htb_ret
