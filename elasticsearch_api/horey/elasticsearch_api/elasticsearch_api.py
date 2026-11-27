"""
Shamelessly stolen from:
https://github.com/lukecyca/pyelasticsearch
"""
import datetime
import json
import os.path
import pdb

from elasticsearch.client.utils import _make_path
from horey.h_logger import get_logger
from horey.elasticsearch_api.elasticsearch_api_configuration_policy import (
    ElasticsearchAPIConfigurationPolicy,
)
from elasticsearch import Elasticsearch
from horey.common_utils.common_utils import CommonUtils
from horey.elasticsearch_api.monitor import Monitor
from horey.elasticsearch_api.destination import Destination

logger = get_logger()


class ElasticsearchAPI(object):
    def __init__(self, configuration: ElasticsearchAPIConfigurationPolicy = None):
        self.client = None
        self.configuration = configuration
        self.connect()
        self.indices = None
        self.monitors = None
        self.destinations = None

    def connect(self):
        # pdb.set_trace()
        self.client = Elasticsearch([self.configuration.server_address])
        self.client.transport
        return

    def init_indices(self):
        indices = self.client.cat.indices(format="json")
        cs_indices = ",".join([index["index"] for index in indices])
        self.indices = self.client.indices.get(cs_indices)

    def get_number_of_shards_used(self):
        shards_counter = 0
        for index_name, index_data in self.indices.items():
            shards_counter += int(index_data["settings"]["index"]["number_of_shards"])
        return shards_counter

    def delete_indices(self, index_names):
        index_names = ",".join(index_names)
        self.client.indices.delete(index_names)

    def clear_indices(self, time_limit=None):
        if time_limit is None:
            time_limit = datetime.datetime.now() - datetime.timedelta(days=30 * 2)

        self.init_indices()
        to_del_indices = []
        for es_index_name, es_index in self.indices.items():
            if es_index_name.startswith("."):
                continue

            created_date = CommonUtils.timestamp_to_datetime(
                es_index["settings"]["index"]["creation_date"], microseconds_value=True
            )
            if created_date < time_limit:
                logger.info(
                    f"Deleting index '{es_index_name}' created at {created_date}"
                )
                to_del_indices.append(es_index_name)
        breakpoint()
        self.client.indices.delete(to_del_indices)
        logger.info(f"Deleted {len(to_del_indices)} out of {len(self.indices)}")

    def recreate_kibana_index(self):
        pdb.set_trace()
        self.client.indices.delete([".kibana"])

        ret = self.client.indices.create(
            ".kibana", body={"mappings": {"dynamic": True}}
        )

    def create_alarm(self):
        """
        _plugins/_alerting/monitors
        @return:
        """
        pdb.set_trace()
        self.client.transport.perform_request(
            "GET", _make_path("Test"), params=None, headers=None
        )

        self.client.transport.perform_request(
            "GET", _make_path("_cat", "indices", None), params=None, headers=None
        )

        self.client.transport.perform_request(
            "POST",
            _make_path("_plugins", "_alerting", "monitors"),
            params=None,
            headers=None,
        )
        self.client.transport.perform_request(
            "GET",
            _make_path("_plugins", "_alerting", "monitors", "alerts"),
            params=None,
            headers=None,
        )
        ""

    def create_monitor(self, monitor):
        """
        https://opensearch.org/docs/latest/monitoring-plugins/alerting/api/#create-query-level-monitor
        @return:
        """
        request = monitor.generate_create_request()
        request["triggers"][0]["actions"] = []
        pdb.set_trace()

        self.client.transport.perform_request(
            "POST",
            _make_path("_plugins", "_alerting", "monitors"),
            params=None,
            headers=None,
            body=request,
        )

    def init_monitors(self, from_cache=False, cache_filename=None):
        if from_cache:
            self.monitors = self.init_objects_from_cache(Monitor, cache_filename)
            return
        search_result = self.client.transport.perform_request(
            "GET",
            _make_path("_plugins", "_alerting", "monitors", "_search"),
            body={"query": {"regexp": {"monitor.name": ".*"}}},
        )
        monitors = []
        for monitor_metadata in search_result["hits"]["hits"]:
            monitor = Monitor()
            monitor.init_from_search_reply(monitor_metadata)
            monitors.append(monitor)
        self.monitors = monitors

    def init_objects_from_cache(self, cls, file_name):
        cache_file_path = os.path.join(self.configuration.cache_dir, file_name)
        with open(cache_file_path, "r") as file_handler:
            objects = json.load(file_handler)

        ret = []
        for dict_obj in objects:
            obj = cls()
            obj.init_from_dict(dict_obj)
            ret.append(obj)

        return ret

    def init_destinations(self):
        search_result = self.client.transport.perform_request(
            "GET", _make_path("_plugins", "_alerting", "destinations")
        )
        destinations = []
        for _metadata in search_result["destinations"]:
            destination = Destination()
            destination.init_from_search_reply(_metadata)
            destinations.append(destination)
        self.destinations = destinations

    def cache_objects(self, objects, file_name):
        pdb.set_trace()
        cache_file_path = os.path.join(self.configuration.cache_dir, file_name)
        ret = []
        for obj in objects:
            ret.append(obj.convert_to_dict())

        with open(cache_file_path, "w") as file_handler:
            json.dump(ret, file_handler)
