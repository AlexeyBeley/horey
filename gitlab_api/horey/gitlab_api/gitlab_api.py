"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json
import pdb

import requests
from horey.h_logger import get_logger
from horey.gitlab_api.gitlab_api_configuration_policy import GitlabAPIConfigurationPolicy

logger = get_logger()


class GitlabAPI:
    def __init__(self, configuration: GitlabAPIConfigurationPolicy = None):
        self.token = configuration.token
        self.group_id = configuration.group_id
        self.base_address = "https://gitlab.com"

    def get(self, request_path):
        request = self.create_request(request_path)
        headers = {}

        if self.token is not None:
            headers["PRIVATE-TOKEN"] = self.token

        response = requests.get(
            request,
            headers=headers
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to gitlab api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def post(self, request_path, data):
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["PRIVATE-TOKEN"] = self.token

        response = requests.post(
            request, data=json.dumps(data),
            headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f'Request to gitlab api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def delete(self, request_path):
        request = self.create_request(request_path)
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.delete(
            request,
            headers=headers
        )
        if response.status_code != 200:
            raise RuntimeError(
                f'Request to gitlab api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def provision_organisation(self, org_name):
        logger.info(f"Provisioning organisation {org_name}")
        response = self.get("/orgs")
        for org in response:
            if org["name"] == org_name:
                logger.info(f"Found organisation: {response}")
                return org["id"]

        response = self.post("/orgs", {"name": org_name})
        logger.info(f"Provisioned organisation: {response}")
        return response["orgId"]

    def add_user_to_organisation(self, org_id, user):
        response = self.get(f"/orgs/{org_id}/users")
        for org in response:
            if org["orgId"] == org_id and org["login"] == user:
                logger.info(f"Found user {user} in organisation: {response}")
                return

        response = self.post(f"/orgs/{org_id}/users", {"loginOrEmail": user, "role": "Admin"})
        logger.info(f"Added user {user} to organisation: {response}")

    def create_request(self, request: str):
        """

        #request = "https://gitlab.com/api/v4/groups/{group_id}/projects"
        @param request:
        @return:
        """
        if request.startswith("/"):
            request = request[1:]

        return f"{self.base_address}/api/v4/groups/{self.group_id}/{request}"

    def init_projects(self):
        for dict_src in self.get("projects"):
            print(dict_src)
            pdb.set_trace()

    def provision_datasource(self, datasource):
        self.post("datasources", datasource.generate_create_request())
