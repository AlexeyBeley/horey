"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import datetime
import json
import requests
from horey.h_logger import get_logger
from horey.bob_api.bob_api_configuration_policy import BobAPIConfigurationPolicy
from horey.bob_api.employee import Employee
from horey.bob_api.timeoff_request import TimeoffRequest

from horey.replacement_engine.replacement_engine import ReplacementEngine

logger = get_logger()


class BobAPI:
    """
    API to work with Grafana 8 API
    """

    def __init__(self, configuration: BobAPIConfigurationPolicy = None):
        self.employees = None

        self.base_address = configuration.server_address
        self.token = configuration.token
        self.replacement_engine = ReplacementEngine()
        self.configuration = configuration

    def get(self, request_path):
        """
        Execute get call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = self.token

        response = requests.get(request, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(
                f"Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def post(self, request_path, data):
        """
        Execute post call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = self.token

        response = requests.post(request, data=json.dumps(data), headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def put(self, request_path, data):
        """
        Execute post call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.put(request, data=json.dumps(data), headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def delete(self, request_path):
        """
        Execute delete call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = self.token

        response = requests.delete(request, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(
                f"Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def create_request(self, request: str):
        """
        Create full request based on relative request
        @param request:
        @return:
        """
        if request.startswith("/"):
            request = request[1:]

        return f"{self.base_address}/{request}"

    def init_employees(self, cache=None, from_cache=False):
        """
        Init employees

        @return:
        """

        if from_cache:
            self.employees = self.init_objects_from_cache(
                self.configuration.employees_cache_file_path, Employee
            )
            return

        ret = self.get("v1/people?humanReadable=false&includeHumanReadable=false")
        self.employees = [Employee(dict_src) for dict_src in ret["employees"]]

        cache = cache if cache is not None else self.configuration.cache

        if cache:
            self.cache_objects(
                self.configuration.employees_cache_file_path, self.employees
            )

    def init_timeoff_requests(self, requested_before=365, cache=None, from_cache=False):
        """
        Init timeoff requests

        @param from_cache:
        @param cache:
        @param requested_before:
        @return:
        """

        if from_cache:
            return self.init_objects_from_cache(
                self.configuration.timeoff_requests_cache_file_path, TimeoffRequest
            )

        date_now = datetime.datetime.now()
        start_date = date_now - datetime.timedelta(days=requested_before)
        ret = self.get(
            f"v1/timeoff/requests/changes?since={start_date.strftime('%Y-%m-%dT00:00-00:00')}"
        )
        timeoff_requests = [TimeoffRequest(dict_src) for dict_src in ret["changes"]]

        cache = cache if cache is not None else self.configuration.cache

        if cache:
            self.cache_objects(
                self.configuration.timeoff_requests_cache_file_path, timeoff_requests
            )

        return timeoff_requests

    @staticmethod
    def init_objects_from_cache(cache_file_path, object_class):
        """
        Init objects from cache

        @return:
        """

        with open(cache_file_path, encoding="utf-8") as file_handler:
            return [object_class(dict_src) for dict_src in json.load(file_handler)]

    @staticmethod
    def cache_objects(cache_file_path, objects):
        """
        Cache objects

        @return:
        """

        with open(cache_file_path, "w", encoding="utf-8") as file_handler:
            json.dump([obj.convert_to_dict() for obj in objects], file_handler)

    def get_reportees(self, manager, recursive=True):
        """
        Get employee's reportees.

        @param manager:
        @param recursive:
        @return:
        """

        ret = []
        for employee in self.employees:
            reports_to = employee.work.get("reportsTo")
            if reports_to is None:
                continue

            if reports_to["displayName"] != manager.display_name:
                continue

            if employee.work.get("directReports") is None:
                ret.append(employee)
                continue

            if not employee.work.get("isManager"):
                raise NotImplementedError(
                    f"{employee.display_name} has directReports but is not isManager"
                )

            if not recursive:
                ret.append(employee)
                continue
            ret += [employee] + self.get_reportees(employee)

        return ret

    def get_current_timeoffs(self, employees=None):
        """
        Get future timeoffs requested last year.

        @return:
        """
        display_names = [employee.display_name for employee in employees]
        timeoff_requests = self.init_timeoff_requests()
        date_now = datetime.datetime.now()
        actual_timeoffs = {}
        for timeoff_request in timeoff_requests:
            if (
                display_names
                and timeoff_request.employee_display_name not in display_names
            ):
                continue

            if timeoff_request.date_end < date_now:
                continue

            if timeoff_request.date_start > date_now:
                continue

            try:
                actual_timeoffs[timeoff_request.employee_display_name].append(
                    timeoff_request
                )
            except KeyError:
                actual_timeoffs[timeoff_request.employee_display_name] = []
                actual_timeoffs[timeoff_request.employee_display_name].append(
                    timeoff_request
                )

        return actual_timeoffs

    def get_future_timeoffs(self, employees=None):
        """
        Get future timeoffs requested last year.

        @return:
        """

        display_names = (
            None
            if employees is None
            else [employee.display_name for employee in employees]
        )

        timeoff_requests = self.init_timeoff_requests(from_cache=True)
        date_now = datetime.datetime.now()

        actual_timeoffs = {}
        for timeoff_request in timeoff_requests:
            if (
                display_names
                and timeoff_request.employee_display_name not in display_names
            ):
                continue

            if timeoff_request.date_end < date_now:
                continue

            try:
                actual_timeoffs[timeoff_request.employee_display_name].append(
                    timeoff_request
                )
            except KeyError:
                actual_timeoffs[timeoff_request.employee_display_name] = []
                actual_timeoffs[timeoff_request.employee_display_name].append(
                    timeoff_request
                )

        return actual_timeoffs

    def get_vacation_report(self, manager):
        """
        Team and company report.

        @param manager:
        @return:
        """
        return_string = "##############################\n"
        team_employees = self.get_reportees(manager)
        dict_ret = self.get_current_timeoffs(employees=[manager] + team_employees)
        if dict_ret:
            return_string += "TEAM VACATIONS:\n"

            for vacations in dict_ret.values():
                vacation = sorted(vacations, key=lambda vacation: vacation.date_end)[-1]
                return_string += vacation.generate_current_vacation_string() + "\n"
            return_string += "END TEAM VACATIONS!\n"
        else:
            return_string += "NO TEAM VACATIONS!\n"

        return_string += "##############################\n"

        dict_ret = self.get_current_timeoffs(employees=self.employees)
        if dict_ret:
            return_string += "COMPANY VACATIONS:\n"

            for vacations in dict_ret.values():
                vacation = sorted(vacations, key=lambda vacation: vacation.date_end)[-1]
                return_string += vacation.generate_current_vacation_string() + "\n"
            return_string += "END COMPANY VACATIONS!\n"
        else:
            return_string += "NO COMPANY VACATIONS!\n"

        return return_string

    def print_employees_per_manager(self):
        """
        Print employees reporting to manager

        @return:
        """
        lst_ret = []
        for manager in self.employees:
            reportees = self.get_reportees(manager, recursive=True)
            len_reportees = len(reportees)
            if len_reportees == 0:
                continue
            lst_ret.append((manager.display_name, len_reportees))

        for pair in sorted(lst_ret, key=lambda x: x[1], reverse=True):
            print(pair)
