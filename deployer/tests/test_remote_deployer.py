"""
Test remote deployer functions.

"""

import os
import shutil
from pathlib import Path
from unittest import mock
import pytest

from horey.deployer.remote_deployer import RemoteDeployer
from horey.deployer.deployment_target import DeploymentTarget
from horey.deployer.deployment_step import DeploymentStep
from horey.common_utils.common_utils import CommonUtils
from horey.deployer.deployment_step_configuration_policy import (
    DeploymentStepConfigurationPolicy,
)

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "horey" / "test_deployer" / "mock_values.py"

mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

deployer = RemoteDeployer()

# pylint: disable = missing-function-docstring


@pytest.fixture(name="target")
def target_fixture():
    target = DeploymentTarget()

    path = Path(target.local_deployment_dir_path)
    if path.exists():
        shutil.rmtree(path)

    shutil.copytree(Path(__file__).parent / "deployment_scripts", path)

    yield target
    shutil.rmtree(path)


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


@pytest.mark.todo
def test_provision_target_remote_deployer_infrastructure_rsa_ed25519key():
    """
    Test zipping mechanism.

    :return:
    """
    target = DeploymentTarget()
    target.local_deployment_dir_path = "/tmp/deployment_test"
    target.deployment_target_ssh_key_type = "ed25519key"
    target.remote_deployment_dir_path = "/tmp/deployment_test"

    target.deployment_target_address = mock_values["target_address_rsa_ed25519key"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_ed25519key"]

    target.bastion_address = mock_values["target_bastion_address"]
    target.bastion_user_name = mock_values["target_username"]
    target.bastion_ssh_key_path = mock_values["target_bastion_ssh_key"]

    os.makedirs(target.remote_deployment_dir_path, exist_ok=True)
    with open(os.path.join(target.remote_deployment_dir_path, "test_file.txt"), "w", encoding="utf-8") as file_handler:
        file_handler.write("some data")
    target.bastion_ssh_key_type = "rsa"
    deployer.provision_target_remote_deployer_infrastructure_raw(target)


@pytest.mark.unit
def test_provision_target_remote_deployer_infrastructure_rsa():
    """
    Test zipping mechanism.

    :return:
    """
    target = DeploymentTarget()
    target.local_deployment_dir_path = "/tmp/deployment_test"
    target.deployment_target_ssh_key_type = "rsa"
    target.remote_deployment_dir_path = "/tmp/deployment_test"

    target.deployment_target_address = mock_values["target_address_with_rsa_key"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_key"]

    target.bastion_address = mock_values["target_bastion_address"]
    target.bastion_user_name = mock_values["target_username"]
    target.bastion_ssh_key_path = mock_values["target_bastion_ssh_key"]

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
    stdout_string, stderr_string = deployer.execute_remote_windows(target, 'powershell -Command "sleep 10; echo 1"')
    assert stdout_string.strip() == "1"
    assert stderr_string == ""


@pytest.mark.unit
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


@pytest.mark.unit
def test_connect_to_target_without_bastion():
    """
    Test zipping mechanism.

    :return:
    """
    client = deployer.connect_to_target(mock_values["target_bastion_address"], mock_values["target_username"], mock_values["target_bastion_ssh_key"])
    command = "ls / | grep tmp | wc -l"

    channel = client.invoke_shell()

    stdin = channel.makefile('wb')
    stdout = channel.makefile('r')
    _, shout, _, _ = deployer.execute_remote_shell(stdin, stdout, command, mock_values["target_bastion_address"])
    assert shout[-1].strip("\n").strip(" ") == "1"


@pytest.mark.unit
def test_connect_to_target_with_bastion():
    """
    Test zipping mechanism.

    :return:
    """

    bastion_client = deployer.connect_to_target(mock_values["target_bastion_address"], mock_values["target_username"], mock_values["target_bastion_ssh_key"])

    address = mock_values["target_address_with_rsa_key"]
    user_name = mock_values["target_username"]
    ssh_key_path = mock_values["target_ssh_key_file_rsa_key"]

    internal_client = deployer.connect_to_target(address, user_name, ssh_key_path, proxy_jump_client=bastion_client)

    channel = internal_client.invoke_shell()

    stdin = channel.makefile('wb')
    stdout = channel.makefile('r')
    command = "ls / | grep tmp | wc -l"
    _, shout, _, _ = deployer.execute_remote_shell(stdin, stdout, command, mock_values["target_bastion_address"])
    assert shout[-1].strip("\n").strip(" ") == "1"


@pytest.mark.unit
def test_get_ssh_client():
    address = mock_values["target_bastion_address"]
    user_name = mock_values["target_username"]
    ssh_key_path = mock_values["target_bastion_ssh_key"]

    internal_client = deployer.get_ssh_client(address, user_name, ssh_key_path)
    for _ in range(10):
        internal_client_new = deployer.get_ssh_client(address, user_name, ssh_key_path)
        assert internal_client_new is internal_client


@pytest.mark.unit
def test_get_ssh_client_with_proxy():
    address = mock_values["target_bastion_address"]
    user_name = mock_values["target_username"]
    ssh_key_path = mock_values["target_bastion_ssh_key"]

    proxy_client = deployer.get_ssh_client(address, user_name, ssh_key_path)

    address = mock_values["target_address_with_rsa_key"]
    user_name = mock_values["target_username"]
    ssh_key_path = mock_values["target_ssh_key_file_rsa_key"]
    internal_client = deployer.get_ssh_client(address, user_name, ssh_key_path, proxy_jump_client=proxy_client, proxy_jump_addr=mock_values["target_bastion_address"])

    for _ in range(10):
        internal_client_new = deployer.get_ssh_client(address, user_name, ssh_key_path, proxy_jump_client=proxy_client, proxy_jump_addr=mock_values["target_bastion_address"])
        assert internal_client_new is internal_client


@pytest.mark.unit
def test_provision_target_remote_deployer_infrastructure_thread(target):
    target.deployment_target_address = mock_values["target_bastion_address"]
    target.deployment_target_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.deployment_target_user_name = mock_values["target_username"]

    deployer.provision_target_remote_deployer_infrastructure_thread(target)
    assert target.remote_deployer_infrastructure_provisioning_finished


@pytest.mark.unit
def test_provision_target_remote_deployer_infrastructure_raw_with_proxy(target):
    target.bastion_address = mock_values["target_bastion_address"]
    target.bastion_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.bastion_user_name = mock_values["target_username"]

    target.deployment_target_address = mock_values["target_address_with_rsa_key"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_key"]

    deployer.provision_target_remote_deployer_infrastructure_raw(target)
    assert target.remote_deployer_infrastructure_provisioning_finished


@pytest.mark.unit
def test_provision_target_remote_deployer_infrastructure_raw_direct(target):
    target.deployment_target_address = mock_values["target_bastion_address"]
    target.deployment_target_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.deployment_target_user_name = mock_values["target_username"]

    deployer.provision_target_remote_deployer_infrastructure_raw(target)
    assert target.remote_deployer_infrastructure_provisioning_finished


@pytest.mark.unit
def test_zip_target_remote_deployer_infrastructure(target):
    target.bastion_address = mock_values["target_bastion_address"]
    target.bastion_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.bastion_user_name = mock_values["target_username"]

    target.deployment_target_address = mock_values["target_address_with_rsa_key"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_key"]

    ret = deployer.zip_target_remote_deployer_infrastructure(target)
    assert ret.exists()


@pytest.mark.unit
def test_deploy_target_step_direct(target):
    target.deployment_target_address = mock_values["target_bastion_address"]
    target.deployment_target_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.deployment_target_user_name = mock_values["target_username"]

    config = DeploymentStepConfigurationPolicy("test-step")
    config.script_name = "test_script_1.sh"
    config.sleep_time = 5
    step = DeploymentStep(config)
    deployer.provision_target_remote_deployer_infrastructure_raw(target)
    deployer.deploy_target_step(target, step)
    assert target.remote_deployer_infrastructure_provisioning_finished


@pytest.mark.unit
def test_deploy_target_step_with_proxy(target):
    target.bastion_address = mock_values["target_bastion_address"]
    target.bastion_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.bastion_user_name = mock_values["target_username"]

    target.deployment_target_address = mock_values["target_address_with_rsa_key"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_key"]
    config = DeploymentStepConfigurationPolicy("test-step")
    config.script_name = "test_script_1.sh"
    config.sleep_time = 5
    step = DeploymentStep(config)
    deployer.provision_target_remote_deployer_infrastructure_raw(target)
    deployer.deploy_target_step(target, step)
    assert target.remote_deployer_infrastructure_provisioning_finished


@pytest.mark.done
def test_wait_to_finish_step_direct(target):
    target.deployment_target_address = mock_values["target_bastion_address"]
    target.deployment_target_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.deployment_target_user_name = mock_values["target_username"]
    config = DeploymentStepConfigurationPolicy("test-step")
    config.script_name = "test_script_1.sh"
    step = DeploymentStep(config)
    deployer.provision_target_remote_deployer_infrastructure_raw(target)
    deployer.deploy_target_step(target, step, asynchronous=True)
    deployer.wait_to_finish_step(target, step)
    assert step.status_code == step.StatusCode.SUCCESS


@pytest.mark.done
def test_wait_to_finish_step_with_proxy(target):
    target.bastion_address = mock_values["target_bastion_address"]
    target.bastion_ssh_key_path = mock_values["target_bastion_ssh_key"]
    target.bastion_user_name = mock_values["target_username"]

    target.deployment_target_address = mock_values["target_address_with_rsa_key"]
    target.deployment_target_user_name = mock_values["target_username"]
    target.deployment_target_ssh_key_path = mock_values["target_ssh_key_file_rsa_key"]
    config = DeploymentStepConfigurationPolicy("test-step")
    config.script_name = "test_script_1.sh"
    config.sleep_time = 5
    step = DeploymentStep(config)
    deployer.provision_target_remote_deployer_infrastructure_raw(target)
    deployer.deploy_target_step(target, step, asynchronous=True)
    deployer.wait_to_finish_step(target, step)
    assert step.status_code == step.StatusCode.SUCCESS
