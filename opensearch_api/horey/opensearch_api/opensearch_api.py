"""
Opensearch API
https://opensearch.org/docs/2.12/api-reference/

"""
import copy
import fnmatch
import json
import os
import pathlib
import time
import uuid

import requests
from horey.h_logger import get_logger
from horey.opensearch_api.opensearch_api_configuration_policy import (
    OpensearchAPIConfigurationPolicy,
)

from horey.opensearch_api.index_pattern import IndexPattern
from horey.opensearch_api.index_management_policy import IndexManagementPolicy
from horey.opensearch_api.monitor import Monitor
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class OpensearchAPI:
    """
    API to work with Opensearch 8 API
    """

    def __init__(self, configuration: OpensearchAPIConfigurationPolicy = None):
        self._monitors = None
        self._index_management_policies = None
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

    @property
    def index_management_policies(self):
        """
        Initialized ISM policies.

        :return:
        """

        if not self._index_management_policies:
            self.init_index_management_policies()
        return self._index_management_policies

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

    def init_index_management_policies(self):
        """
        Init ISM policies.

        @return:
        """

        ret = self.get("_plugins/_ism/policies", data={"size": 10000})
        if len(ret["policies"]) < ret["total_policies"]:
            raise NotImplementedError('len(ret["policies"]) < ret["total_policies"]')

        self._index_management_policies = []
        for hit in ret["policies"]:
            policy = IndexManagementPolicy(hit["policy"])
            policy.id = hit["_id"]
            policy.seq_no = hit["_seq_no"]
            policy.primary_term = hit["_primary_term"]
            self._index_management_policies.append(policy)
        return self._index_management_policies

    def update_index_management_policy_information(self, policy: IndexManagementPolicy) -> bool:
        """
        Update policy attributes from the existing policy with the same policy_id.
        Fetches the current state to get fresh seq_no and primary_term.

        :param policy:
        :return: False if there is no existing policy with this policy_id.
        """

        current_policies = CommonUtils.find_objects_by_values(self.init_index_management_policies(),
                                                              {"policy_id": policy.policy_id})
        if len(current_policies) > 1:
            raise RuntimeError(current_policies)

        if not current_policies:
            return False

        policy.__dict__.update(copy.deepcopy(current_policies[0].__dict__))
        return True

    def provision_index_management_policy(self, policy: IndexManagementPolicy):
        """
        Create or update.

        :return:
        """

        current_policy = IndexManagementPolicy({"policy_id": policy.policy_id})
        if not self.update_index_management_policy_information(current_policy):
            logger.info(f"Creating index management policy {policy.policy_id}")
            self.put(f"_plugins/_ism/policies/{policy.policy_id}", policy.generate_create_request())
            self._index_management_policies = []
        elif request := current_policy.generate_update_request(policy):
                logger.info(f"Updating index management policy {current_policy.policy_id}")
                self.put(f"_plugins/_ism/policies/{current_policy.policy_id}"
                        f"?if_seq_no={current_policy.seq_no}&if_primary_term={current_policy.primary_term}",
                            request)
                self._index_management_policies = []

        self.apply_index_management_policy_to_existing_indices(policy)
        self.validate_index_management_policy_template(policy)
        return True

    @staticmethod
    def _get_ism_template_index_patterns(policy: IndexManagementPolicy):
        """
        Unique index patterns from policy.ism_template.

        :param policy:
        :return:
        """

        ism_templates = policy.ism_template or []
        if isinstance(ism_templates, dict):
            ism_templates = [ism_templates]

        index_patterns = []
        for ism_template in ism_templates:
            for index_pattern in ism_template.get("index_patterns", []):
                if index_pattern not in index_patterns:
                    index_patterns.append(index_pattern)
        return index_patterns

    def validate_index_management_policy_template(self, policy: IndexManagementPolicy, timeout=60, interval=2):
        """
        Create a temporary index matching the policy's ism_template, verify the policy was attached
        to it automatically and delete the index.

        :param policy:
        :param timeout: Seconds to wait for ISM to attach the policy (it is done asynchronously).
        :param interval:
        :return: True. Raises RuntimeError if the policy was not attached.
        """

        index_patterns = [pattern for pattern in self._get_ism_template_index_patterns(policy)
                          if not pattern.startswith("-")]
        if not index_patterns:
            return True

        suffix = f"tmp-ism-validation-{uuid.uuid4().hex[:8]}"
        index_name = index_patterns[0].replace("*", suffix)
        if not fnmatch.fnmatchcase(index_name, index_patterns[0]):
            raise ValueError(f"Can not generate a temporary index name for pattern: {index_patterns[0]}")

        logger.info(f"Validating index management policy {policy.policy_id} with temporary index {index_name}")
        self.put(index_name, {})
        try:
            policy_id_keys = ["index.plugins.index_state_management.policy_id",
                              "index.opendistro.index_state_management.policy_id",
                              "policy_id"]
            deadline = time.monotonic() + timeout
            attached_policy_id = None
            while True:
                explain = self.get(f"_plugins/_ism/explain/{index_name}").get(index_name, {})
                attached_policy_id = next((explain[key] for key in policy_id_keys if explain.get(key)), None)
                if attached_policy_id or time.monotonic() >= deadline:
                    break
                time.sleep(interval)
        finally:
            logger.info(f"Deleting temporary index {index_name}")
            self.delete(index_name)

        if attached_policy_id != policy.policy_id:
            raise RuntimeError(f"New index {index_name} did not get policy {policy.policy_id} from the ism_template, "
                               f"attached policy: {attached_policy_id}")

        return True

    def apply_index_management_policy_to_existing_indices(self, policy: IndexManagementPolicy):
        """
        ISM templates are applied only to newly created indices.
        Attach the policy to the already existing indices matching the policy's ism_template index patterns.
        Indices already managed by a policy are skipped by ISM and are not changed.

        :param policy:
        :return: Number of indices the policy was attached to.
        """

        index_patterns = self._get_ism_template_index_patterns(policy)
        if not index_patterns:
            return 0

        response = self.post(f"_plugins/_ism/add/{','.join(index_patterns)}", {"policy_id": policy.policy_id})
        for failed_index in response.get("failed_indices", []):
            logger.info(f"Policy {policy.policy_id} was not applied to index "
                        f"{failed_index.get('index_name')}: {failed_index.get('reason')}")

        updated_indices = response.get("updated_indices", 0)
        logger.info(f"Applied index management policy {policy.policy_id} to {updated_indices} existing indices")
        return updated_indices

    def dispose_index_management_policy(self, policy: IndexManagementPolicy):
        """
        Erase policy.

        :return:
        """

        current_policies = CommonUtils.find_objects_by_values(self.index_management_policies,
                                                              {"policy_id": policy.policy_id})
        if len(current_policies) > 1:
            raise RuntimeError(current_policies)

        if len(current_policies) == 1:
            logger.info(f"Disposing index management policy {current_policies[0].policy_id}")
            self.delete(f"_plugins/_ism/policies/{current_policies[0].policy_id}")
            self._index_management_policies = []

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

    def get_notification_channels_slugs(self):
        ret = self.get(f"_plugins/_notifications/channels")

    def get_index_templates_raw(self):
        ret = self.get(f"_index_template")

    def get_notification_channels(self):
        not_configs = self.get("_plugins/_notifications/configs")
        return not_configs["config_list"]

    def provision_notification_channel(self, data):
        return self.post("/_plugins/_notifications/configs/", data=data)

    def init_notification_channels(self):
        """
        List channels

        @return:
        """

        ret = self.get("/_plugins/_notifications/channels")

        return ret["channel_list"]

    def init_notification_configs(self):
        """
        Fetch configs

        @return:
        """

        ret = self.get("_plugins/_notifications/configs")
        return ret["config_list"]

    def backup(self, dst_dir: pathlib.Path):
        """
        Backup config.

        :param dst_dir:
        :return:
        """

        os.makedirs(dst_dir, exist_ok=True)

        self.init_monitors()

        monitor_sources = [mon.dict_src for mon in self.monitors]
        with open(dst_dir / "monitors.json", "w", encoding="UTF-8") as fh:
            json.dump(monitor_sources, fh)

        configs = self.init_notification_configs()
        with open(dst_dir / "notification_configs.json", "w", encoding="UTF-8") as fh:
            json.dump(configs, fh)

    def restore(self, dst_dir: pathlib.Path):
        configs = self.init_notification_configs()
        if len(configs) != 1:
            raise NotImplementedError("""with open(dst_dir / "notification_configs.json", "w", encoding="UTF-8") as fh: json.dump(configs, fh) """)

        with open(dst_dir / "monitors.json", "r", encoding="UTF-8") as fh:
            lst_src = json.load(fh)
        monitors = [Monitor(dict_src) for dict_src in lst_src]
        for monitor in monitors:
            monitor.triggers[0]["query_level_trigger"]["actions"][0]["destination_id"] = configs[0]["config"]["name"]
            self.provision_monitor(monitor)

    def create_user(self, user_name, password, roles):
        """
        Create user.

        :param user_name:
        :param password:
        :param roles:
        :return:
        """

        request = {
            "password": password,
            "opendistro_security_roles": roles,
            "backend_roles": []
        }
        return self.put(f"_plugins/_security/api/internalusers/{user_name}", request)
