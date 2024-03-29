"""
Test remote deployer functions.

"""

import os
from unittest import mock
import pytest

tests_dir = os.path.dirname(os.path.abspath(__file__))

from horey.deployer.remote_deployer import RemoteDeployer
from horey.deployer.deployment_target import DeploymentTarget
from horey.common_utils.common_utils import CommonUtils

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "mock_values.py")
)
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

deployer = RemoteDeployer()

@pytest.mark.done
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

@pytest.mark.done
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

@pytest.mark.done
def test_provision_indirect_remote_deployer_infrastructure_ubuntu22_rsa():
    """
    Test zipping mechanism.

    :return:
    """
    target = DeploymentTarget()

    target.deployment_target_address = mock_values["indirect_target_address_rsa_ubuntu_22"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["indirect_target_ssh_key_file_rsa_ubuntu_22"]
    target.local_deployment_dir_path = mock_values["deployment_dir_path"]
    target.deployment_target_ssh_key_type = "rsa"

    target.bastion_address = mock_values["target_address_rsa_ubuntu_22"]
    target.bastion_user_name = mock_values["target_username"]
    target.bastion_ssh_key_path = mock_values["target_ssh_key_file_rsa_ubuntu_22"]

    target.remote_deployment_dir_path = "/tmp/deployment_test"
    os.makedirs(target.remote_deployment_dir_path, exist_ok=True)
    with open(os.path.join(target.remote_deployment_dir_path, "test_file.txt"), "w", encoding="utf-8") as file_handler:
        file_handler.write("some data")
    target.bastion_ssh_key_type = "rsa"
    deployer.provision_target_remote_deployer_infrastructure_raw(target)

@pytest.mark.done
def test_provision_direct_remote_deployer_infrastructure_ubuntu22_rsa():
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


@pytest.mark.done
def test_indirect_remote_deployer_execute_remote_windows():
    """
    Test zipping mechanism.

    :return:
    """
    target = DeploymentTarget()
    target.deployment_target_address = mock_values["target_address_windows"]
    target.deployment_target_user_name = mock_values["target_windows_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_windows"]
    target.local_deployment_dir_path = mock_values["deployment_dir_path"]
    target.deployment_target_ssh_key_type = "rsa"

    target.remote_deployment_dir_path = "/tmp/deployment_test"
    # bastion
    target.bastion_address = mock_values["bastion_1_address"]
    target.bastion_user_name = mock_values["bastion_1_username"]
    target.bastion_ssh_key_path = mock_values["target_ssh_key_file_rsa_ubuntu_22"]
    target.bastion_ssh_key_type = "rsa"
    os.makedirs(target.remote_deployment_dir_path, exist_ok=True)
    with open(os.path.join(target.remote_deployment_dir_path, "test_file.txt"), "w", encoding="utf-8") as file_handler:
        file_handler.write("some data")
    target.bastion_ssh_key_type = "rsa"
    ret = deployer.execute_remote_windows(target, 'powershell -Command "sleep 10; echo 1"')
    assert ret.strip() == "1"

@pytest.mark.wip
def test_indirect_remote_deployer_put_file_windows():
    """
    Test zipping mechanism.

    :return:
    """
    target = DeploymentTarget()
    target.deployment_target_address = mock_values["target_address_windows"]
    target.deployment_target_user_name = mock_values["target_windows_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_windows"]
    target.local_deployment_dir_path = mock_values["deployment_dir_path"]
    target.deployment_target_ssh_key_type = "rsa"

    target.remote_deployment_dir_path = "/tmp/deployment_test"
    # bastion
    target.bastion_address = mock_values["bastion_1_address"]
    target.bastion_user_name = mock_values["bastion_1_username"]
    target.bastion_ssh_key_path = mock_values["target_ssh_key_file_rsa_ubuntu_22"]
    target.bastion_ssh_key_type = "rsa"
    os.makedirs(target.remote_deployment_dir_path, exist_ok=True)
    with open(os.path.join(target.remote_deployment_dir_path, "test_file.txt"), "w", encoding="utf-8") as file_handler:
        file_handler.write("some data")
    target.bastion_ssh_key_type = "rsa"

    ret = deployer.put_file_windows(target, __file__, r"C:\\tmp\\py.txt")

    assert ret
