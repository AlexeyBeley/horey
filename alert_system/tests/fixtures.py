import os
import shutil

import pytest
from horey.alert_system.alert_system_configuration_policy import AlertSystemConfigurationPolicy
from horey.alert_system.alert_system import AlertSystem


@pytest.fixture(name="alert_system_configuration")
def fixture_alert_system_configuration():
    as_configuration = AlertSystemConfigurationPolicy()
    as_configuration.horey_repo_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )

    as_configuration.region = "us-west-2"
    as_configuration.lambda_name = "alert_system_test_deploy_lambda"
    as_configuration.sns_topic_name = "topic_test_alert_system"
    as_configuration.notification_channels = ["notification_channel_echo_initializer.py"]
    as_configuration.tags = [{"Key": "env_level", "Value": "development"}]

    as_configuration.deployment_dir_path = "/tmp/horey_deployment_alert_system"
    as_configuration.active_deployment_validation = True

    #with open(alert_system_config_file_path, "w") as file_handler:
    #    json.dump(dict_config, file_handler)
    if os.path.exists(as_configuration.deployment_dir_path):
        shutil.rmtree(as_configuration.deployment_dir_path)
    os.makedirs(as_configuration.deployment_dir_path)

    yield as_configuration

    shutil.rmtree(as_configuration.deployment_dir_path)

