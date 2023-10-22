"""
Testing opensearch API
"""
import os
import pytest

from horey.opensearch_api.opensearch_api import OpensearchAPI
from horey.opensearch_api.opensearch_api_configuration_policy import (
    OpensearchAPIConfigurationPolicy,
)

ignore_dir_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore"
)
configuration = OpensearchAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(ignore_dir_path, "opensearch", "opensearch_api_configuration_values.py")
)
configuration.init_from_file()

opensearch_api = OpensearchAPI(configuration=configuration)


# pylint: disable= missing-function-docstring


@pytest.mark.skip
def test_init_opensearch_api():
    """
    Test Opensearch API initiation
    @return:
    """
    _opensearch_api = OpensearchAPI(configuration=configuration)
    assert isinstance(_opensearch_api, OpensearchAPI)


@pytest.mark.skip
def test_init_monitors():
    """
    Test dashboard object provisioning
    @return:
    """

    ret = opensearch_api.init_monitors()
    assert len(ret) > 0


@pytest.mark.skip
def test_post_document():
    response = opensearch_api.post_document("veggies",
                                 {
                                     "name": "beet",
                                     "color": "red",
                                     "classification": "root"
                                 })
    assert response.get("_id") is not None

@pytest.mark.wip
def test_init_index_patterns():
    """
    Test dashboard object provisioning
    @return:
    """

    ret = opensearch_api.init_index_patterns()
    assert len(ret) > 0

@pytest.mark.done
def test_put_index_pattern():
    response = opensearch_api.put_index_pattern("test-template", ["veggies"])
    assert response.get("acknowledged")
