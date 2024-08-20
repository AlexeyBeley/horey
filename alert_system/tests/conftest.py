"""
Module used by pytest to configure environment.

"""

import os
from pathlib import Path

import pytest
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy

# pylint: disable=missing-function-docstring


@pytest.fixture(name="alert_system_configuration")
def fixture_alert_system_configuration():
    as_configuration = AlertSystemConfigurationPolicy()
    as_configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )

    as_configuration.region = "us-west-2"
    as_configuration.lambda_name = "alert_system_test_deploy_lambda"
    as_configuration.sns_topic_name = "topic_test_alert_system"
    as_configuration.notification_channels = [os.path.join(os.path.dirname(__file__),
                                                           "notification_channels",
                                                           "notification_channel_echo_initializer.py")]
    as_configuration.tags = [{"Key": "env_level", "Value": "development"}]
    as_configuration.active_deployment_validation = False

    os.makedirs(as_configuration.deployment_directory_path, exist_ok=True)
    yield as_configuration


@pytest.fixture(name="alert_system_configuration_file_path_with_echo")
def fixture_alert_system_configuration_file_path_with_echo(alert_system_configuration):
    config_file_path = os.path.join(alert_system_configuration.deployment_directory_path, "as_config.json")
    alert_system_configuration.generate_configuration_file(config_file_path)
    yield config_file_path


@pytest.fixture(name="alert_system_configuration_file_path_message_override_notify_echo")
def fixture_alert_system_configuration_file_path_message_override_notify_echo(alert_system_configuration):
    alert_system_configuration.message_classes = [str(Path(".").parent.joinpath("message_override.py"))]
    config_file_path = os.path.join(alert_system_configuration.deployment_directory_path, "as_config.json")
    alert_system_configuration.generate_configuration_file(config_file_path)
    yield config_file_path


@pytest.fixture(name="alert_system_configuration_file_path_with_slack")
def fixture_alert_system_configuration_file_path_with_slack():
    as_configuration = AlertSystemConfigurationPolicy()
    as_configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )

    as_configuration.region = "us-west-2"
    as_configuration.lambda_name = "alert_system_test_deploy_lambda"
    as_configuration.sns_topic_name = "topic_test_alert_system"
    as_configuration.notification_channels = [os.path.join(os.path.dirname(__file__),
                                                           "notification_channels",
                                                           "notification_channel_slack_initializer.py")]
    as_configuration.tags = [{"Key": "env_level", "Value": "development"}]
    as_configuration.active_deployment_validation = False

    os.makedirs(as_configuration.deployment_directory_path, exist_ok=True)
    config_file_path = os.path.join(as_configuration.deployment_directory_path, "as_config.json")
    as_configuration.generate_configuration_file(config_file_path)
    yield config_file_path
