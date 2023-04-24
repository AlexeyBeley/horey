"""
Manage Azure Devops

"""

import json
import datetime
from collections import defaultdict

import requests
from horey.common_utils.text_block import TextBlock
from horey.h_logger import get_logger
from horey.azure_devops_api.azure_devops_api_configuration_policy import (
    AzureDevopsAPIConfigurationPolicy,
)

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

    def print(self):
        """
        Print the object.

        :return:
        """

        for field_name, field_value in self.dict_src.items():
            print(f"--> {field_name}: {field_value}")


class WorkItem(AzureDevopsObject):
    """
    Work item -task, user story, feature, epic etc.
    """
    def __init__(self, dict_src):
        self.fields = {}
        super().__init__(dict_src)

    def print(self):
        """
        Print the fields.

        :return:
        """

        for field_name, field_value in self.fields.items():
            print(f"--> {field_name}: {field_value}")

    @property
    def title(self):
        """
        WI title

        :return:
        """

        return self.dict_src["fields"]["System.Title"]

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

        return self.dict_src["fields"]["System.IterationPath"]

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
            self._start_date = datetime.datetime.strptime(self.dict_src["attributes"]["startDate"], "%Y-%m-%dT%H:%M:%SZ")
        return self._start_date

    @property
    def finish_date(self):
        """
        End date.

        :return:
        """

        if self._finish_date is None:
            self._finish_date = datetime.datetime.strptime(self.dict_src["attributes"]["finishDate"], "%Y-%m-%dT%H:%M:%SZ")
        return self._finish_date

    def get_hours(self, only_remaining=True):
        """
        Get hours of the spirnt.

        :param only_remaining:
        :return:
        """

        now = datetime.datetime.now()
        hours = 0
        start = self.start_date
        if only_remaining:
            if self.finish_date < now:
                return 0
            if self.start_date < now < self.finish_date:
                hours = max(min(17 - datetime.datetime.now().hour, 6), 0)
                start = datetime.datetime(year=now.year, month=now.month, day=now.day+1)

        daygenerator = (start + datetime.timedelta(days=x) for x in range((self.finish_date - start).days))
        days = sum(1 for day in daygenerator if day.weekday() in [0, 1, 2, 3, 6])
        for str_date, off_hours in self.VACATIONS.items():
            if self.start_date < datetime.datetime.strptime(str_date, "%Y-%m-%d") < self.finish_date:
                hours -= off_hours

        return hours + days*6


class Backlog(AzureDevopsObject):
    """
    Standard.
    """


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
        self.work_items = []
        self.team_members = []
        self.iterations = []
        self.backlogs = []
        self.processes = []

    def get_iteration(self, date_find=None):
        """
        Get current by default or find by date specified.

        :param date_find:
        :return:
        """

        if not self.iterations:
            self.init_iterations()
        if date_find is None:
            date_find = datetime.datetime.now()
        for iteration in self.iterations:
            if iteration.start_date <= date_find <= iteration.finish_date:
                return iteration
        raise RuntimeError("Can not find current iteration.")

    def init_iterations(self, cache_file_path=None):
        """
        Fetch from API

        :return:
        """

        if cache_file_path is not None:
            with open(cache_file_path, encoding="utf-8") as file_handler:
                lst_src = json.load(file_handler)
            self.iterations = [Iteration(dict_src) for dict_src in lst_src]
            return self.iterations

        lst_ret = []
        response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/teamsettings/iterations?api-version=7.0")
        ret = response.json()
        logger.info("Start fetching iterations")
        for iteration in ret["value"]:
            response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/teamsettings/iterations/{iteration['id']}?api-version=7.0")
            dict_src = response.json()
            lst_ret.append(Iteration(dict_src))

        self.iterations = lst_ret
        logger.info(f"Inited {len(lst_ret)} iterations")
        return lst_ret

    def init_dashboards(self):
        """
        Fetch from API

        :return:
        """

        lst_ret = []
        response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/dashboard/dashboards?api-version=7.0-preview.3")
        ret = response.json()
        for dashboard in ret["value"]:
            response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/dashboard/dashboards/{dashboard['id']}?api-version=7.0-preview.3")
            ret = response.json()
            lst_ret.append(ret)
        return lst_ret

    def init_boards(self):
        """
        Fetch from API

        :return:
        """

        lst_ret = []
        response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/boards?api-version=7.0")
        ret = response.json()
        for board in ret["value"]:
            response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/boards/{board['id']}?api-version=7.0")
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

    def init_backlogs(self, cache_file_path=None):
        """
        Fetch from API

        :return:
        """

        if cache_file_path is not None:
            with open(cache_file_path, encoding="utf-8") as file_handler:
                lst_src = json.load(file_handler)
            lst_ret = [Backlog(dict_src) for dict_src in lst_src]
            self.backlogs = lst_ret
            return lst_ret

        project = self.project_name
        organization = self.org_name
        response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/backlogs?api-version=7.0")
        ret = response.json()
        lst_src = ret["value"]

        lst_ret = []
        logger.info("Start fetching backlogs")
        for backlog in lst_src:
            str_id = backlog["id"]
            response = self.session.get(f"https://dev.azure.com/{organization}/{project}/{self.team_name}/_apis/work/backlogs/{str_id}?api-version=7.0")
            dict_src = response.json()
            lst_ret.append(Backlog(dict_src))
        logger.info(f"Inited {len(lst_ret)} backlogs")

        self.backlogs = lst_ret
        return self.backlogs

    def init_work_items(self, cache_file_path=None):
        """
        Fetch from API

        :return:
        """
        lst_all = []
        if cache_file_path is not None:
            with open(cache_file_path, encoding="utf-8") as file_handler:
                lst_src = json.load(file_handler)
            lst_ret = [WorkItem(dict_src) for dict_src in lst_src]
            self.work_items = lst_ret
            return lst_ret

        if not self.backlogs:
            self.init_backlogs()

        project = self.project_name
        organization = self.org_name
        for backlog_id in [backlog.id for backlog in self.backlogs]:
            response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/backlogs/{backlog_id}/workItems?api-version=7.0")
            ret = response.json()
            lst_src = ret["workItems"]

            lst_ret = []
            logger.info("Starting to fetch work items")
            for work_item in lst_src:
                str_id = work_item["target"]["id"]
                response = self.session.get(f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{str_id}?$expand=all&api-version=7.0")
                dict_src = response.json()
                # dict_src["backlog_id"] = backlog_id
                lst_ret.append(WorkItem(dict_src))
            logger.info(f"Inited {len(lst_ret)} work items with backlog_id: {backlog_id}")
            lst_all += lst_ret

        self.work_items = lst_all
        return self.work_items

    @staticmethod
    def cache(objects, file_path):
        """
        Cache objects with dict_src

        :param objects:
        :param file_path:
        :return:
        """

        lst_ret = [obj.dict_src for obj in objects]
        with open(file_path, "w", encoding="utf-8") as file_handler:
            json.dump(lst_ret, file_handler)

    def init_team_members(self):
        """
        Fetch from API
        https://learn.microsoft.com/en-us/rest/api/azure/devops/core/teams/get-team-members-with-extended-properties?view=azure-devops-rest-5.0&tabs=HTTP

        :return:
        """

        response = self.session.get(f"https://dev.azure.com/{self.org_name}/_apis/projects/{self.project_name}/teams/{self.team_name}/members?api-version=7.0")
        ret = response.json()
        logger.info("Start fetching team member")

        self.team_members = ret["value"]

    def get(self, request_path):
        """
        Perform get request.

        :param request_path:
        :param is_link:
        :return:
        """

        request = request_path
        response = requests.get(request, headers={"Content-Type": "application/json"}, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(
                f"Request to chronograf api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def post(self, request_path, data):
        """
        Perform post request.

        :param request_path:
        :param data:
        :param is_link:
        :return:
        """
        request = request_path
        response = requests.post(
            request, data=json.dumps(data), headers={"Content-Type": "application/json"}, timeout=30
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Request to chronograf api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

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

        next_iteration_work_items = [work_item for work_item in future_iterations_work_items if work_item.iteration_path == next_iteration.path]
        current_iteration_hours = current_iteration.get_hours()
        next_iteration_hours = next_iteration.get_hours()
        total_hours = current_iteration_hours + next_iteration_hours
        work_items_by_worker = self.split_work_items_by_worker(current_iteration_work_items+next_iteration_work_items)

        for worker_name, work_items in work_items_by_worker.items():
            total_remaining_hours = sum(work_item.get_remaining_work(default=3.0) for work_item in work_items)
            if total_hours < total_remaining_hours:
                h_tb.lines.append(f"Worker {worker_name} has {total_remaining_hours} remaining tasks' hours but only {total_hours} working hours left")

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
