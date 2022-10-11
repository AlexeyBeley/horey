"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import datetime
import json

import requests
from horey.h_logger import get_logger
from horey.bob_api.bob_api_configuration_policy import BobAPIConfigurationPolicy

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

        response = requests.get(
            request,
            headers=headers
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}'
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

        response = requests.post(
            request, data=json.dumps(data),
            headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f'Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}'
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

        response = requests.put(
            request, data=json.dumps(data),
            headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f'Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}'
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

        response = requests.delete(
            request,
            headers=headers
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to grafana api returned an error {response.status_code}, the response is:\n{response.text}'
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

    def init_employees(self, cache=False, from_cache=False):
        """
        Init employees

        @return:
        """
        if from_cache:
            with open(self.configuration.employees_cache_file_path, encoding="utf-8") as file_handler:
                self.employees = json.load(file_handler)
                return

        ret = self.get("v1/people?humanReadable=false&includeHumanReadable=false")
        self.employees = ret["employees"]
        if cache:
            with open(self.configuration.employees_cache_file_path, "w", encoding="utf-8") as file_handler:
                json.dump(self.employees, file_handler)

    def get_reportees(self, display_name, recursive=True):
        """

        @param display_name:
        @param recursive:
        @return:
        """
        ret = []
        for employee in self.employees:
            reports_to = employee["work"].get("reportsTo")
            if reports_to is None:
                continue

            if reports_to["displayName"] != display_name:
                continue

            if employee["work"].get("directReports") is None:
                ret.append(employee)
                continue

            if not employee["work"].get("isManager"):
                raise NotImplementedError(f"{employee['displayName']} has directReports but is not isManager")

            if not recursive:
                ret.append(employee)
                continue
            ret += self.get_reportees(employee["displayName"])

        return ret

    def get_future_timeoffs(self):
        """
        Get future timeoffs requested last year.

        @return:
        """
        ret = self.get("v1/people?humanReadable=false&includeHumanReadable=false")
        self.employees = ret["employees"]

        date_now = datetime.datetime.now()
        start_date = date_now - datetime.timedelta(days=365)
        start_date.strftime("%Y-%m-%dT00:00-00:00")
        ret = self.get(f"v1/timeoff/requests/changes?since={start_date.strftime('%Y-%m-%dT00:00-00:00')}")
        timeoff_requests = ret["changes"]
        actual_timeoffs = []
        for timeoff_request in timeoff_requests:
            end_date = timeoff_request.get("endDate")
            if not end_date:
                end_date = timeoff_request.get("date")
            timeoff_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if timeoff_date < date_now:
                continue
            actual_timeoffs.append(timeoff_request)
        return actual_timeoffs
