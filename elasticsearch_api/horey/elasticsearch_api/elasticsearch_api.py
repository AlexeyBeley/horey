"""
Shamelessly stolen from:
https://github.com/lukecyca/pyelasticsearch
"""
import datetime
import pdb

from horey.h_logger import get_logger
from horey.elasticsearch_api.elasticsearch_api_configuration_policy import ElasticsearchAPIConfigurationPolicy 
from elasticsearch import Elasticsearch
from horey.common_utils.common_utils import CommonUtils

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

    def delete_indices(self, index_names):
        index_names = ",".join(index_names)
        self.client.indices.delete(index_names)

    def clear_indices(self, time_limit=None):
        if time_limit is None:
            time_limit = datetime.datetime.now() - datetime.timedelta(days=30*2)

        self.init_indices()
        to_del_indices = []
        for es_index_name, es_index in self.indices.items():
            created_date = CommonUtils.timestamp_to_datetime(es_index["settings"]["index"]["creation_date"], microseconds_value=True)
            if created_date < time_limit:
                logger.info(f"Deleting index '{es_index_name}' created at {created_date}")
                to_del_indices.append(es_index_name)

        self.client.indices.delete(to_del_indices)
        logger.info(f"Deleted {len(to_del_indices)} out of {len(self.indices)}")
