"""
Init and cache AWS objects.

"""
from pathlib import Path

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.alerts_api_configuration_policy import AlertsAPIConfigurationPolicy
# Uncomment next line to save error lines to /tmp/error.log
logger = get_logger()

aws_api = AWSAPI()


# pylint: disable= missing-function-docstring


@pytest.fixture(name="alerts_api")
def fixture_alerts_api():

    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.project_name = "hry"
    env_configuration.project_name_abbr = "hry"
    env_configuration.environment_level = "development"
    env_configuration.environment_name = "test"
    env_configuration.region = "us-west-2"
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    alerts_api_configuration = AlertsAPIConfigurationPolicy()
    alerts_api_configuration.slug = "has3-test"
    alerts_api = infrastructure_api.get_alerts_api(alerts_api_configuration, environment_api)

    yield alerts_api


@pytest.mark.wip
def test_provision_alert_system(alerts_api):
    alerts_api.aws_lambda_api.build_api.horey_git_api.configuration.branch_name = None
    alerts_api.aws_lambda_api.build_api.horey_git_api.configuration.git_directory_path = Path(__file__).parent.parent.parent.parent
    ret = alerts_api.provision_alert_system()

    assert ret
