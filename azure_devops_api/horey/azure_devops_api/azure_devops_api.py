"""
Manage tasks

"""

import json

import requests
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

    def init_backlogs(self):
        """
        Fetch from API

        :return:
        """
        response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/backlogs?api-version=7.1-preview.1")
        ret = response.json()
        for value in ret["value"]:
            print(value)
        # backlogId = "Microsoft.RequirementCategory"
        backlogId = "Microsoft.TaskCategory"
        response = self.session.get(f"https://dev.azure.com/{self.org_name}/{self.project_name}/{self.team_name}/_apis/work/backlogs/{backlogId}/workItems?api-version=7.0")
        print(response)
        str_id = "1xxx76"
        organization = self.org_name
        project = self.project_name
        response = self.session.get(f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{str_id}?api-version=7.0")
        print(response)

        logger.info("Initializing chronograf sources")

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
