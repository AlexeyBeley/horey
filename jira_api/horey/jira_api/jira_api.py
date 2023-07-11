"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json

import requests
from horey.h_logger import get_logger
from horey.jira_api.jira_api_configuration_policy import (
    JiraAPIConfigurationPolicy,
)
from horey.replacement_engine.replacement_engine import ReplacementEngine

logger = get_logger()


class JiraAPI:
    """
    API to work with Jira 8 API
    """

    def __init__(self, configuration: JiraAPIConfigurationPolicy = None):
        self.dashboards = []
        self.folders = []
        self.datasources = []
        self.rule_namespaces = {}

        self.base_address = configuration.server_address
        self.token = configuration.token
        self.replacement_engine = ReplacementEngine()

    def get(self, request_path):
        """
        Execute get call
        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.get(request, headers=headers, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(
                f"Request to jira api returned an error {response.status_code}, the response is:\n{response.text}"
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
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.post(request, data=json.dumps(data), headers=headers, timeout=60)

        if response.status_code != 200:
            raise RuntimeError(
                f"Request to jira api returned an error {response.status_code}, the response is:\n{response.text}"
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

        response = requests.put(request, data=json.dumps(data), headers=headers, timeout=60)

        if response.status_code != 200:
            raise RuntimeError(
                f"Request to jira api returned an error {response.status_code}, the response is:\n{response.text}"
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
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.delete(request, headers=headers, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(
                f"Request to jira api returned an error {response.status_code}, the response is:\n{response.text}"
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

        return f"{self.base_address}/api/{request}"
