"""
Test remote deployer functions.

"""

import os
from unittest import mock

tests_dir = os.path.dirname(os.path.abspath(__file__))

from horey.deployer.remote_deployer import RemoteDeployer
from horey.deployer.deployment_target import DeploymentTarget
from horey.common_utils.common_utils import CommonUtils

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "mock_values.py")
)
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


def test_provision_target_remote_deployer_infrastructure_rsa_ed25519key():
    """
    Test zipping mechanism.

    :return:
    """
    target = DeploymentTarget()
    target.deployment_target_address = mock_values["target_address_rsa_ed25519key"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_ed25519key"]
    target.local_deployment_dir_path = mock_values["deployment_dir_path"]
    target.deployment_target_ssh_key_type = "ed25519key"

    target.bastion_address = mock_values["target_bastion_address"]
    target.bastion_user_name = mock_values["target_username"]
    target.bastion_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.remote_deployment_dir_path = "/tmp/deployment_test"
    os.makedirs(target.remote_deployment_dir_path, exist_ok=True)
    with open(os.path.join(target.remote_deployment_dir_path, "test_file.txt"), "w", encoding="utf-8") as file_handler:
        file_handler.write("some data")
    target.bastion_ssh_key_type = "rsa"
    deployer.provision_target_remote_deployer_infrastructure_raw(target)


def test_provision_bastion_remote_deployer_infrastructure_ubuntu22_rsa():
    """
    Test zipping mechanism.

    :return:
    """
    target = DeploymentTarget()
    target.deployment_target_address = mock_values["target_address_rsa_ubuntu_22"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_ubuntu_22"]
    target.local_deployment_dir_path = mock_values["deployment_dir_path"]
    target.deployment_target_ssh_key_type = "rsa"

    target.remote_deployment_dir_path = "/tmp/deployment_test"
    os.makedirs(target.remote_deployment_dir_path, exist_ok=True)
    with open(os.path.join(target.remote_deployment_dir_path, "test_file.txt"), "w", encoding="utf-8") as file_handler:
        file_handler.write("some data")
    target.bastion_ssh_key_type = "rsa"
    deployer.provision_target_remote_deployer_infrastructure_raw(target)


if __name__ == "__main__":
    # test_provision_target_remote_deployer_infrastructure_raw()
    # test_provision_target_remote_deployer_infrastructure_rsa_ed25519key()
    test_provision_bastion_remote_deployer_infrastructure_ubuntu22_rsa()
