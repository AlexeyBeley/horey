import os
import sys
import pdb
from unittest import mock
import pytest
sys.path.insert(0, os.path.abspath("../horey/deployer"))

tests_dir = os.path.dirname(os.path.abspath(__file__))

from deployment_step import DeploymentStep


def test_update_finish_status():
    configuration_mock = mock.Mock()
    configuration_mock.finish_status_file_name = "status_success_file"
    step = DeploymentStep(configuration_mock)
    step.update_finish_status(tests_dir)
    assert step.status_code == step.StatusCode.SUCCESS

    configuration_mock.finish_status_file_name = "status_failure_file"
    step = DeploymentStep(configuration_mock)
    step.update_finish_status(tests_dir)
    assert step.status_code == step.StatusCode.FAILURE

    configuration_mock.finish_status_file_name = "status_error_file"
    step = DeploymentStep(configuration_mock)
    step.update_finish_status(tests_dir)
    assert step.status_code == step.StatusCode.ERROR

    configuration_mock.finish_status_file_name = "not_existing_file"
    step = DeploymentStep(configuration_mock)
    step.update_finish_status(tests_dir)
    assert step.status_code == step.StatusCode.ERROR


def test_update_finish_status_tmp():
    step = DeploymentStep(None)
    os_path_exists_mock = mock.Mock()
    os_path_exists_mock.return_value = True

    with mock.patch("open", file_mock):
        step.update_finish_status()


def test_update_output():
    configuration_mock = mock.Mock()
    configuration_mock.output_file_name = "status_success_file"
    step = DeploymentStep(configuration_mock)
    step.update_output(tests_dir)
    assert step.output == "SUCCESS"


if __name__ == "__main__":
    test_update_output()

