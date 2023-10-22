"""
Opensearch API
"""
import json

import requests
from horey.h_logger import get_logger
from horey.opensearch_api.opensearch_api_configuration_policy import (
    OpensearchAPIConfigurationPolicy,
)

from horey.opensearch_api.index_pattern import IndexPattern

logger = get_logger()



class OpensearchAPI:
    """
    API to work with Opensearch 8 API
    """

    def __init__(self, configuration: OpensearchAPIConfigurationPolicy = None):
        self.monitors = []
        self.configuration = configuration
        self.index_patterns = []
        self.headers = {"Content-Type": "application/json; charset=utf-8"}

    def get(self, request_path):
        """
        Execute get call
        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        response = requests.get(request, auth=(self.configuration.user, self.configuration.password),
                                 headers=self.headers, timeout=60)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to opensearch api returned an error {response.status_code}, the response is:\n{response.text}"
            )

        return response

    def post(self, request_path, data):

        """
        Execute post call

        @param data:
        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        response = requests.post(request, auth=(self.configuration.user, self.configuration.password),
                                 data=json.dumps(data), headers=self.headers, timeout=60)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to opensearch api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def put(self, request_path, data):
        """
        Execute put call

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        response = requests.put(request, auth=(self.configuration.user, self.configuration.password),
                                 data=json.dumps(data), headers=self.headers, timeout=60)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to opensearch api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

    def delete(self, request_path):
        """
        Execute delete call
        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        response = requests.delete(request, auth=(self.configuration.user, self.configuration.password), headers=self.headers, timeout=60)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to opensearch api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response


    def create_request(self, request: str):
        """
        Create full request based on relative request
        @param request:
        @return:
        """

        if request.startswith("/"):
            request = request[1:]

        return f"{self.configuration.server_address}/{request}"

    def init_monitors(self):
        """
        Init Monitors
        search = {
            "query": {
                "match": {
                    "monitor.name": "*"
                }
            }
        }
        ret = requests.get(f"{self.configuration.server_address}/_plugins/_alerting/monitors/_search", json=search,
                           auth=(self.configuration.user, self.configuration.password), headers=self.headers)

        breakpoint()
        @return:
        """
        print(self)
        return []


    def init_index_patterns(self):
        """
        Fetch and init.

        :return:
        """

        ret = self.get(f"{self.configuration.server_address}/_index_template")

        dict_src = ret.json()
        self.index_patterns = [IndexPattern(index_template) for index_template in dict_src["index_templates"]]
        return self.index_patterns

    def provision_monitor(self):
        """

        :return:
        """

    def post_document(self, index_name, data):
        """

        :param index_name:
        :param data:
        :return:
        """

        return self.post(f"{index_name}/_doc", data)

    def put_index_pattern(self, template_name, index_patterns):
        """

        :param template_name:
        :param index_patterns:
        :return:
        """

        request = {
            "index_patterns": index_patterns,
            "data_stream": {},
            "priority": 100
        }

        return self.put(f"_index_template/{template_name}", request)
