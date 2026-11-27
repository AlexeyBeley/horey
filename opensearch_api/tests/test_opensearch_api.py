"""
Testing opensearch API
"""
import json
import os
from pathlib import Path
from unittest import mock

import pytest

from horey.opensearch_api.index_management_policy import IndexManagementPolicy
from horey.opensearch_api.opensearch_api import OpensearchAPI
from horey.opensearch_api.opensearch_api_configuration_policy import (
    OpensearchAPIConfigurationPolicy,
)

ignore_dir_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore"
)

# Change per project.
PROJECT_PREFIX = "horey"
POLICY_ID = f"{PROJECT_PREFIX}-retention"

# pylint: disable= missing-function-docstring


@pytest.fixture(name="opensearch_api")
def fixture_opensearch_api():
    configuration = OpensearchAPIConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(ignore_dir_path, "opensearch", "opensearch_api_configuration_values.py")
    )
    configuration.init_from_file()

    yield OpensearchAPI(configuration=configuration)


@pytest.fixture(name="opensearch_api_ng")
def fixture_opensearch_api_ng():
    configuration = OpensearchAPIConfigurationPolicy()
    configuration.configuration_file_full_path = os.path.abspath(
        os.path.join(ignore_dir_path, "opensearch", "opensearch_api_configuration_values.py")
    )
    configuration.init_from_file()

    yield OpensearchAPI(configuration=configuration)


@pytest.fixture(name="offline_opensearch_api")
def fixture_offline_opensearch_api():
    """
    API without a server: tests patch the "get" calls.
    """

    yield OpensearchAPI(configuration=mock.Mock(server_address="https://localhost:9200"))


def generate_ism_policies_response(*policy_ids):
    """
    Response of GET _plugins/_ism/policies.
    """

    policies = []
    for seq_no, policy_id in enumerate(policy_ids, start=1):
        policy = IndexManagementPolicy.init_from_retention(policy_id, 3, f"{policy_id}-*")
        policies.append({"_id": policy_id,
                         "_seq_no": seq_no,
                         "_primary_term": 2,
                         "policy": policy.dict_src})

    return {"policies": policies, "total_policies": len(policies)}


@pytest.mark.unit
def test_update_index_management_policy_information_found(offline_opensearch_api):
    response = generate_ism_policies_response("other-policy", POLICY_ID)
    policy = IndexManagementPolicy({"policy_id": POLICY_ID})

    with mock.patch.object(offline_opensearch_api, "get", return_value=response):
        assert offline_opensearch_api.update_index_management_policy_information(policy) is True

    assert policy.id == POLICY_ID
    assert policy.seq_no == 2
    assert policy.primary_term == 2
    assert policy.default_state == "hot"
    assert policy.ism_template[0]["index_patterns"] == [f"{POLICY_ID}-*"]
    assert policy.states[0]["transitions"][0]["conditions"]["min_index_age"] == "90d"


@pytest.mark.unit
def test_update_index_management_policy_information_not_found(offline_opensearch_api):
    response = generate_ism_policies_response("other-policy")
    policy = IndexManagementPolicy({"policy_id": POLICY_ID})

    with mock.patch.object(offline_opensearch_api, "get", return_value=response):
        assert offline_opensearch_api.update_index_management_policy_information(policy) is False

    assert policy.id is None
    assert policy.seq_no is None
    assert policy.states is None
    assert policy.dict_src == {"policy_id": POLICY_ID}


@pytest.mark.unit
def test_update_index_management_policy_information_duplicates(offline_opensearch_api):
    response = generate_ism_policies_response(POLICY_ID, POLICY_ID)
    policy = IndexManagementPolicy({"policy_id": POLICY_ID})

    with mock.patch.object(offline_opensearch_api, "get", return_value=response):
        with pytest.raises(RuntimeError):
            offline_opensearch_api.update_index_management_policy_information(policy)


@pytest.mark.unit
def test_update_index_management_policy_information_does_not_share_state(offline_opensearch_api):
    response = generate_ism_policies_response(POLICY_ID)
    policy = IndexManagementPolicy({"policy_id": POLICY_ID})

    with mock.patch.object(offline_opensearch_api, "get", return_value=response):
        offline_opensearch_api.update_index_management_policy_information(policy)

    policy.states[0]["name"] = "changed"
    assert response["policies"][0]["policy"]["states"][0]["name"] == "hot"


# Integration tests against the live opensearch (opensearch_api_ng).
# A dedicated policy id and an index pattern that matches no real index are used,
# so existing policies are never touched and no real index gets the test policy attached.
LIVE_POLICY_ID = f"{PROJECT_PREFIX}-retention-integration-test"


@pytest.fixture(name="live_policy")
def fixture_live_policy(opensearch_api_ng):
    """
    Create the test policy on the live server and erase it after the test.
    """

    policy = IndexManagementPolicy.init_from_retention(LIVE_POLICY_ID, 3, f"{LIVE_POLICY_ID}-*")
    opensearch_api_ng.provision_index_management_policy(policy)
    yield policy
    opensearch_api_ng.dispose_index_management_policy(policy)


@pytest.mark.unit
def test_update_index_management_policy_information_live_found(opensearch_api_ng, live_policy):
    policy = IndexManagementPolicy({"policy_id": LIVE_POLICY_ID})

    assert opensearch_api_ng.update_index_management_policy_information(policy) is True

    assert policy.id == LIVE_POLICY_ID
    assert isinstance(policy.seq_no, int)
    assert isinstance(policy.primary_term, int)
    assert policy.default_state == "hot"
    assert policy.ism_template[0]["index_patterns"] == [f"{LIVE_POLICY_ID}-*"]
    assert policy.states[0]["transitions"][0]["conditions"]["min_index_age"] == "90d"
    assert policy.generate_update_request(live_policy) is None


@pytest.mark.unit
def test_update_index_management_policy_information_live_not_found(opensearch_api_ng):
    policy = IndexManagementPolicy({"policy_id": f"{LIVE_POLICY_ID}-does-not-exist"})

    assert opensearch_api_ng.update_index_management_policy_information(policy) is False

    assert policy.id is None
    assert policy.seq_no is None
    assert policy.states is None
    assert policy.dict_src == {"policy_id": f"{LIVE_POLICY_ID}-does-not-exist"}


@pytest.mark.unit
def test_update_index_management_policy_information_live_does_not_share_state(opensearch_api_ng, live_policy):
    policy = IndexManagementPolicy({"policy_id": LIVE_POLICY_ID})
    assert opensearch_api_ng.update_index_management_policy_information(policy)

    policy.states[0]["name"] = "changed"

    fresh_policy = IndexManagementPolicy({"policy_id": LIVE_POLICY_ID})
    assert opensearch_api_ng.update_index_management_policy_information(fresh_policy)
    assert fresh_policy.states[0]["name"] == "hot"


# Provision and dispose integration tests. A separate policy id from the one above is used.
LIVE_PROVISION_POLICY_ID = f"{LIVE_POLICY_ID}-provision"


@pytest.fixture(name="absent_live_policy_id")
def fixture_absent_live_policy_id(opensearch_api_ng):
    """
    Guarantee the test policy does not exist before the test and erase it after the test.
    """

    policy = IndexManagementPolicy({"policy_id": LIVE_PROVISION_POLICY_ID})
    opensearch_api_ng.dispose_index_management_policy(policy)
    yield LIVE_PROVISION_POLICY_ID
    opensearch_api_ng.dispose_index_management_policy(policy)


def fetch_live_policy(opensearch_api, policy_id):
    """
    Fetch the current state of the policy from the live server. None if absent.
    """

    policy = IndexManagementPolicy({"policy_id": policy_id})
    if not opensearch_api.update_index_management_policy_information(policy):
        return None
    return policy


@pytest.mark.unit
def test_provision_index_management_policy_live_create(opensearch_api_ng, absent_live_policy_id):
    assert fetch_live_policy(opensearch_api_ng, absent_live_policy_id) is None

    desired = IndexManagementPolicy.init_from_retention(absent_live_policy_id, 3, f"{absent_live_policy_id}-*")
    assert opensearch_api_ng.provision_index_management_policy(desired) is True

    current = fetch_live_policy(opensearch_api_ng, absent_live_policy_id)
    assert current is not None
    assert current.states[0]["transitions"][0]["conditions"]["min_index_age"] == "90d"
    assert current.ism_template[0]["index_patterns"] == [f"{absent_live_policy_id}-*"]


@pytest.mark.unit
def test_provision_index_management_policy_live_update(opensearch_api_ng, absent_live_policy_id):
    desired = IndexManagementPolicy.init_from_retention(absent_live_policy_id, 3, f"{absent_live_policy_id}-*")
    assert opensearch_api_ng.provision_index_management_policy(desired)
    seq_no_created = fetch_live_policy(opensearch_api_ng, absent_live_policy_id).seq_no

    desired = IndexManagementPolicy.init_from_retention(absent_live_policy_id, 6, f"{absent_live_policy_id}-*")
    assert opensearch_api_ng.provision_index_management_policy(desired) is True

    current = fetch_live_policy(opensearch_api_ng, absent_live_policy_id)
    assert current.states[0]["transitions"][0]["conditions"]["min_index_age"] == "180d"
    assert current.seq_no > seq_no_created


@pytest.mark.unit
def test_provision_index_management_policy_live_no_change(opensearch_api_ng, absent_live_policy_id):
    desired = IndexManagementPolicy.init_from_retention(absent_live_policy_id, 3, f"{absent_live_policy_id}-*")
    assert opensearch_api_ng.provision_index_management_policy(desired)
    seq_no_created = fetch_live_policy(opensearch_api_ng, absent_live_policy_id).seq_no

    assert opensearch_api_ng.provision_index_management_policy(desired) is True

    assert fetch_live_policy(opensearch_api_ng, absent_live_policy_id).seq_no == seq_no_created


@pytest.mark.unit
def test_dispose_index_management_policy_live(opensearch_api_ng, absent_live_policy_id):
    desired = IndexManagementPolicy.init_from_retention(absent_live_policy_id, 3, f"{absent_live_policy_id}-*")
    assert opensearch_api_ng.provision_index_management_policy(desired)
    assert fetch_live_policy(opensearch_api_ng, absent_live_policy_id) is not None

    assert opensearch_api_ng.dispose_index_management_policy(desired) is True

    assert fetch_live_policy(opensearch_api_ng, absent_live_policy_id) is None


@pytest.mark.unit
def test_dispose_index_management_policy_live_absent(opensearch_api_ng, absent_live_policy_id):
    policy = IndexManagementPolicy({"policy_id": absent_live_policy_id})

    assert opensearch_api_ng.dispose_index_management_policy(policy) is True

    assert fetch_live_policy(opensearch_api_ng, absent_live_policy_id) is None


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


@pytest.mark.unit
def test_restore(opensearch_api_ng):
    """
    Test dashboard object provisioning

    @return:
    """

    ret = opensearch_api_ng.restore(Path("/opt/backup_opensearch"))

@pytest.mark.unit
def test_restore(opensearch_api_ng):
    """
    Test dashboard object provisioning

    @return:
    """

    ret = opensearch_api_ng.create_user("test1", "P@ssword1", ["readall", "opensearch_dashboards_user"])
