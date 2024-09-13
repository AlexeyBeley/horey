"""
Opensearch API
https://opensearch.org/docs/2.12/api-reference/

"""
import json

import requests
from horey.h_logger import get_logger
from horey.opensearch_api.opensearch_api_configuration_policy import (
    OpensearchAPIConfigurationPolicy,
)

from horey.opensearch_api.index_pattern import IndexPattern
from horey.opensearch_api.monitor import Monitor
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class OpensearchAPI:
    """
    API to work with Opensearch 8 API
    """

    def __init__(self, configuration: OpensearchAPIConfigurationPolicy = None):
        self._monitors = None
        self.configuration = configuration
        if self.configuration.server_address.endswith("/"):
            self.configuration.server_address = self.configuration.server_address[:-1]

        self.index_patterns = []
        self.headers = {"Content-Type": "application/json; charset=utf-8"}

    @property
    def monitors(self):
        """
        Initialized monitors.

        :return:
        """

        if not self._monitors:
            self.init_monitors()
        return self._monitors

    def get(self, request_path, data=None):
        """
        Execute get call
        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)

        response = requests.get(request, auth=(self.configuration.user, self.configuration.password),
                                headers=self.headers, timeout=60, json=data)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to opensearch api returned an error {response.status_code}, the response is:\n{response.text}"
            )

        return response.json()

    def post(self, request_path, data):

        """
        Execute post call

        @param data: dict
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

        response = requests.delete(request, auth=(self.configuration.user, self.configuration.password),
                                   headers=self.headers, timeout=60)

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

        @return:
        """
        search = {
            "query": {
                "exists": {
                    "field": "monitor"
                }
            },
            "size": 10000
        }

        ret = self.get("_plugins/_alerting/monitors/_search", data=search)
        self._monitors = []
        if len(ret["hits"]["hits"]) < ret["hits"]["total"]["value"]:
            raise NotImplementedError('len(ret["hits"]["hits"]) < ret["hits"]["total"]["value"]:')
        for hit in ret["hits"]["hits"]:
            if list(hit.keys()) != ["_index", "_id", "_version", "_seq_no", "_primary_term", "_score", "_source"]:
                raise NotImplementedError(hit)
            monitor = Monitor(hit["_source"])
            monitor.id = hit["_id"]
            self._monitors.append(monitor)
        return self._monitors

    def init_index_patterns(self):
        """
        Fetch and init.

        :return:
        """

        dict_src = self.get("_index_template")

        self.index_patterns = [IndexPattern(index_template) for index_template in dict_src["index_templates"]]
        return self.index_patterns

    def provision_monitor(self, monitor: Monitor):
        """
        Create or update.

        :return:
        """

        current_monitors = CommonUtils.find_objects_by_values(self.monitors, {"name": monitor.name})
        if len(current_monitors) > 1:
            raise RuntimeError(current_monitors)

        if len(current_monitors) == 1:
            if request := current_monitors[0].generate_update_request(monitor):
                logger.info(f"Updating monitor {current_monitors[0].name}")
                self.put(f"_plugins/_alerting/monitors/{current_monitors[0].id}", request)
                self._monitors = []
            return True

        logger.info(f"Creating monitor {monitor.name}")
        self.post("_plugins/_alerting/monitors", data=monitor.generate_create_request())
        self._monitors = []
        return True

    def dispose_monitor(self, monitor: Monitor):
        """
        Erase monitor.

        :return:
        """

        current_monitors = CommonUtils.find_objects_by_values(self.monitors, {"name": monitor.name})
        if len(current_monitors) > 1:
            raise RuntimeError(current_monitors)

        if len(current_monitors) == 1:
            logger.info(f"Disposing monitor {current_monitors[0].name}")
            self.delete(f"_plugins/_alerting/monitors/{current_monitors[0].id}")

        return True

    def post_document(self, index_name, data):
        """

        :param index_name:
        :param data:
        :return:
        """

        return self.post(f"{index_name}/_doc", data)

    def put_index_template(self, template_name, index_patterns):
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

    def put_index_pattern(self, pattern_name):
        """

        :param pattern_name:
        :return:
        """

        request = {
            "index_pattern": {
            "title": pattern_name,
            "timeFieldName": "@timestamp"}
        }

        return self.put(f"_index_patterns/{pattern_name}", request)

    def get_all_index_patterns(self):
        """

        :return:
        """

        return self.get("_index_patterns")
