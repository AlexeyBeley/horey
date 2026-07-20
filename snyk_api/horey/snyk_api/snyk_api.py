"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json
import shutil
from pathlib import Path

import requests
from horey.h_logger import get_logger
from horey.snyk_api.snyk_api_configuration_policy import (
    SnykAPIConfigurationPolicy,
)

logger = get_logger()


class SnykAPI:
    """
    Main Class.
    """

    def __init__(self, configuration: SnykAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.server_address = "https://api.snyk.io"

    def create_request(self, request: str):
        """
        Construct request.

        #request = "https://github.com/api/v4/groups/{group_id}/projects"
        @param request:
        @return:
        """

        if request.startswith("/"):
            request = request[1:]

        return f"{self.server_address}/{request}"

    def get(self, request_path):
        """
        Compose and send GET request.

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        headers = {"Authorization": self.configuration.api_key}
        response = requests.get(request, headers=headers)
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return response.text


    def post(self, request_path, data):
        """
        Compose and send POST request

        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)
        return self.post_raw(request, data)

    def post_raw(self, request, data):
        """
        Send POST request.

        @param request:
        @param data:
        @return:
        """

        headers = {"Authorization": f"Bearer {self.configuration.pat}",
                   "Content-Type": "application/vnd.github+json",
                   "Accept": "application/vnd.github+json"}

        response = requests.post(request, data=json.dumps(data), headers=headers)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to github api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def put(self, request_path, data):
        """
        Compose and send POST request

        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)
        headers = {"Authorization": f"Bearer {self.configuration.pat}",
                   "Content-Type": "application/vnd.github+json",
                   "Accept": "application/vnd.github+json"}

        response = requests.put(request, data=json.dumps(data), headers=headers)
        response.raise_for_status()

    def delete(self, request_path):
        """
        Compose and send DELETE request

        @param request_path:
        @return:
        """
        request = self.create_request(request_path)
        headers = {"Authorization": f"Bearer {self.configuration.pat}",
                   "Content-Type": "application/vnd.github+json",
                   "Accept": "application/vnd.github+json"}

        response = requests.delete(request, headers=headers)
        response.raise_for_status()


    def get_projects(self):
        """
        Get all projects in org

        :return: 
        """

        projects = self.get(f"/rest/orgs/{self.configuration.org_id}/projects?version=2026-03-25")

        return projects

    def get_targets(self):
        """
        Get all targets in org

        :return:
        """

        projects = self.get(f"/rest/orgs/{self.configuration.org_id}/targets?version=2026-03-25")

        return projects

    def get_integrations(self):
        """
        Get all targets in org

        :return:
        """

        projects = self.get(f"/v1/org/{self.configuration.org_id}/integrations")

        return projects



