import os
import sys
from unittest import mock
from pytest import raises
import pytest
import argparse
import pdb

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "configuration_policies"),
)


from jenkins_configuration_policy import JenkinsConfigurationPolicy


def test_init():
    assert isinstance(JenkinsConfigurationPolicy(), JenkinsConfigurationPolicy)


@pytest.fixture
def configuration_policy():
    configuration_policy = JenkinsConfigurationPolicy()
    return configuration_policy


def test_init_jenkins_deploy_local_configuration_policy(configuration_policy):
    jenkins_hostname = "my_hostname"
    test_args = [
        "my_script_name",
        "--grade",
        "LOCAL",
        "--jenkins_host",
        jenkins_hostname,
    ]

    with mock.patch("sys.argv", test_args):
        configuration_policy.init_from_command_line()
    assert configuration_policy.grade == "LOCAL"
    assert configuration_policy.jenkins_host == jenkins_hostname


def test_init_jenkins_deploy_stg_configuration_policy(configuration_policy):
    test_args = ["my_script_name", "--grade", "STG"]

    with mock.patch("sys.argv", test_args):
        configuration_policy.init_from_command_line()
    assert configuration_policy.grade == "STG"
    assert configuration_policy.jenkins_host == "jenkins-stg"


def test_init_jenkins_deploy_stg_configuration_policy_raises_on_setting_hostname(
    configuration_policy,
):
    jenkins_hostname = "my_hostname"
    test_args = ["my_script_name", "--grade", "STG", "--jenkins_host", jenkins_hostname]

    with mock.patch("sys.argv", test_args):
        with raises(ValueError):
            configuration_policy.init_from_command_line()
