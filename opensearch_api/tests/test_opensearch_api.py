"""
Testing opensearch API
"""
import json
import os
from pathlib import Path

import pytest

from horey.opensearch_api.opensearch_api import OpensearchAPI
from horey.opensearch_api.opensearch_api_configuration_policy import (
    OpensearchAPIConfigurationPolicy,
)

ignore_dir_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore"
)

# pylint: disable= missing-function-docstring


@pytest.fixture(name="opensearch_api")
def fixture_opensearch_api():
    configuration = OpensearchAPIConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(ignore_dir_path, "opensearch", "opensearch_api_configuration_values_eu.py")
    )
    configuration.init_from_file()

    yield OpensearchAPI(configuration=configuration)


@pytest.fixture(name="opensearch_api_ng")
def fixture_opensearch_api_ng():
    configuration = OpensearchAPIConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(ignore_dir_path, "opensearch", "opensearch_api_configuration_values_ng.py")
    )
    configuration.init_from_file()

    yield OpensearchAPI(configuration=configuration)


@pytest.mark.done
def test_init_opensearch_api():
    """
    Test Opensearch API initiation
    @return:
    """
    configuration = OpensearchAPIConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(ignore_dir_path, "opensearch", "opensearch_api_configuration_values_eu.py")
    )
    _opensearch_api = OpensearchAPI(configuration=configuration)
    assert isinstance(_opensearch_api, OpensearchAPI)


@pytest.mark.done
def test_provision_notification_channel(opensearch_api):
    data = {
        "config_id": "sample-id",
        "name": "sample-name",
        "config": {
            "name": "Sample Slack Channel",
            "description": "This is a Slack channel",
            "config_type": "sns",
            "is_enabled": True,
            'sns': {}
        }
    }
    assert opensearch_api.provision_notification_channel(data)


@pytest.mark.unit
def test_init_monitors(opensearch_api):
    ret = opensearch_api.init_monitors()
    assert len(ret) > 0


@pytest.mark.unit
def test_provision_monitor(opensearch_api):
    monitor_current = opensearch_api.monitors[0]
    monitor = monitor_current.copy()
    monitor.name = "test"
    opensearch_api.provision_monitor(monitor)
    assert len(opensearch_api.monitors) > 0


@pytest.mark.done
def test_provision_monitor_disable(opensearch_api):
    monitor_current = opensearch_api.monitors[0]
    monitor = monitor_current.copy()
    monitor.enabled = False
    opensearch_api.provision_monitor(monitor)
    monitor.name = "test"
    opensearch_api.provision_monitor(monitor)
    assert len(opensearch_api.monitors) > 0


@pytest.mark.done
def test_dispose_monitor(opensearch_api):
    monitor_current = opensearch_api.monitors[0]
    monitor = monitor_current.copy()
    monitor.name = "test"
    opensearch_api.dispose_monitor(monitor)
    assert len(opensearch_api.monitors) > 0


@pytest.mark.skip
def test_post_document(opensearch_api):
    response = opensearch_api.post_document("veggies",
                                            {
                                                "name": "beet",
                                                "color": "red",
                                                "classification": "root"
                                            })
    assert response.get("_id") is not None


@pytest.mark.unit
def test_init_index_patterns(opensearch_api):
    """
    Test dashboard object provisioning
    @return:
    """

    ret = opensearch_api.init_index_patterns()
    assert len(ret) > 0


@pytest.mark.done
def test_put_index_pattern(opensearch_api):
    response = opensearch_api.put_index_pattern("test-template", ["veggies"])
    assert response.get("acknowledged")


@pytest.mark.unit
def test_get_index_template_raw(opensearch_api):
    """
    Test dashboard object provisioning
    @return:
    """

    ret = opensearch_api.get_index_templates_raw()
    with open("index_templates_raw.json", "w+") as file_handler:
        json.dump(ret, file_handler)
    assert len(ret) > 0


@pytest.mark.unit
def test_backup(opensearch_api):
    """
    Test dashboard object provisioning

    @return:
    """

    ret = opensearch_api.backup(Path("/opt/backup_opensearch"))


@pytest.mark.wip
def test_restore(opensearch_api_ng):
    """
    Test dashboard object provisioning

    @return:
    """

    ret = opensearch_api_ng.restore(Path("/opt/backup_opensearch"))
