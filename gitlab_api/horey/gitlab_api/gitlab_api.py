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
        self.projects = []
        self.token = configuration.token
        self.group_id = configuration.group_id
        self.base_address = "https://gitlab.com"

    def get(self, request_path):
        request = self.create_request(request_path)
        return self.get_raw(request)

    def get_raw(self, request):
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
        return self.post_raw(request, data)

    def post_raw(self, request, data):
        headers = {"Content-Type": "application/json"}

        if self.token is not None:
            headers["PRIVATE-TOKEN"] = self.token

        response = requests.post(
            request, data=json.dumps(data),
            headers=headers)

        if response.status_code not in [200, 201]:
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
        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f'Request to gitlab api returned an error {response.status_code}, the response is:\n{response.text}'
            )
        return response.json()

    def create_request(self, request: str):
        """

        #request = "https://gitlab.com/api/v4/groups/{group_id}/projects"
        @param request:
        @return:
        """
        if request.startswith("/"):
            request = request[1:]

        return f"{self.base_address}/api/v4/{request}"

    def init_projects(self):
        for dict_src in self.get(f"groups/{self.group_id}/projects"):
            self.projects.append(dict_src)

    def add_user_to_projects(self, projects, user_id):
        for dict_src in projects:
            ret = self.get_raw(dict_src["_links"]["members"])
            if user_id in str(ret):
                continue
            #pdb.set_trace()
            data = {"user_id": user_id, "access_level": 40}
            try:
                self.post(f"projects/{dict_src['id']}/members", data)
                logger.info(f"Added to {dict_src['name']}")
            except Exception as inst:
                logger.error(f"{dict_src['name']} : {repr(inst)}")
                if "An error 403" not in repr(inst):
                    raise
        pdb.set_trace()


    def provision_datasource(self, datasource):
        self.post("datasources", datasource.generate_create_request())
