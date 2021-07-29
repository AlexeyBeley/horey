"""
Shamelessly stolen from:
https://github.com/lukecyca/pyelasticsearch
"""
import pdb

import requests
import json
from horey.h_logger import get_logger
from horey.elasticsearch_api.elasticsearch_api_configuration_policy import ElasticsearchAPIConfigurationPolicy 
from elasticsearch import Elasticsearch
from datetime import datetime

logger = get_logger()


class ElasticsearchAPI(object):
    def __init__(self, configuration: ElasticsearchAPIConfigurationPolicy = None):
        self.client = None
        self.connect(configuration)
        self.indices = None

    def connect(self, configuration):
        self.client = Elasticsearch([configuration.server_address])
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

    def delete_indices(self):
        todel = []
        for index_name, index_data in self.indices.items():
            if "asdASDFSDAS" in index_name:
                todel.append(index_name)
        cs_indices = ",".join(todel)
        self.client.indices.delete(cs_indices)
