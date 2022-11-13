"""
Test remote deployer functions.

"""

import os
from unittest import mock

tests_dir = os.path.dirname(os.path.abspath(__file__))

from horey.deployer.remote_deployer import RemoteDeployer
from horey.common_utils.common_utils import CommonUtils

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

deployer = RemoteDeployer()


def test_provision_target_remote_deployer_infrastructure_raw():
    """
    Test zipping mechanism.

    :return:
    """

    target_mock = mock.Mock()
    target_mock.deployment_target_address = mock_values["target_address"]
    target_mock.deployment_target_user_name = mock_values["target_username"]
    target_mock.deployment_target_ssh_key_path = mock_values["target_ssh_key_file"]
    target_mock.local_deployment_dir_path = mock_values["deployment_dir_path"]
    target_mock.bastion_address = None
    target_mock.remote_deployment_dir_path = "/tmp/deployment_test"
    deployer.provision_target_remote_deployer_infrastructure_raw(target_mock)


if __name__ == "__main__":
    test_provision_target_remote_deployer_infrastructure_raw()