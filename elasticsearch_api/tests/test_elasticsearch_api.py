import pdb

import pytest
import os
import sys

sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))

from horey.elasticsearch_api.elasticsearch_api import ElasticsearchAPI
from horey.elasticsearch_api.elasticsearch_api_configuration_policy import ElasticsearchAPIConfigurationPolicy
from horey.h_logger import get_logger


configuration_values_file_full_path = None
logger = get_logger(configuration_values_file_full_path=
                    configuration_values_file_full_path)

configuration = ElasticsearchAPIConfigurationPolicy()
configuration.configuration_file_full_path = \
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "..", "..", "ignore", "elasticsearch_api_configuration_values.py"))
configuration.init_from_file()

elasticsearch_api = ElasticsearchAPI(configuration=configuration)


# region done
#@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_indices():
    elasticsearch_api.init_indices()
    logger.info(f"len(indexes) = {len(elasticsearch_api.indices)}")
    logger.info(list(elasticsearch_api.indices.keys()))
    assert isinstance(elasticsearch_api.indices, dict)


def test_delete_indices():
    elasticsearch_api.init_indices()
    elasticsearch_api.delete_indices()


def test_get_number_of_shards_used():
    elasticsearch_api.init_indices()
    shards_count = elasticsearch_api.get_number_of_shards_used()
    print(shards_count)
    pdb.set_trace()


def test_clear_indices():
    elasticsearch_api.init_indices()
    elasticsearch_api.clear_indices()

# endregion


if __name__ == "__main__":
    test_init_indices()
    #test_clear_indices()

