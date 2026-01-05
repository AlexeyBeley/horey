"""
Init and cache AWS objects.

"""
import os.path

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.email_api_configuration_policy import EmailAPIConfigurationPolicy
from pathlib import Path
# Uncomment next line to save error lines to /tmp/error.log
logger = get_logger()

aws_api = AWSAPI()


# pylint: disable= missing-function-docstring
configs_dir = Path(".").resolve().parent.parent.parent / "ignore" / "infrastructure_api"
real_life_env_configuration = str(configs_dir / "01_env_api_configs.json")
real_life_email_configuration = str(configs_dir / "email_api_configs.json")

real_life_env_configuration = str(configs_dir / "00_env_api_configs.json")
real_life_email_configuration = str(configs_dir / "email_api_configs.json")

#assert os.path.exists(real_life_env_configuration)
#assert os.path.exists(real_life_email_configuration)


@pytest.fixture(name="email_api")
def fixture_email_api():
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.configuration_file_full_path = real_life_env_configuration
    env_configuration.init_from_file()
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    email_api_configuration = EmailAPIConfigurationPolicy()
    email_api_configuration.configuration_file_full_path = real_life_email_configuration
    email_api_configuration.init_from_file()
    email_api = infrastructure_api.get_email_api(email_api_configuration, environment_api)
    yield email_api


@pytest.mark.unit
def test_init_environment(email_api):
    ret = email_api.send_email("test.horey@horey.com")
    assert ret


@pytest.mark.unit
def test_get_suppressed_emails(email_api):
    ret = email_api.get_suppressed_emails()
    for x in ret:
        print(x)
    assert ret


@pytest.mark.unit
def test_unsupress_email(email_api):
    email_addr = ""
    ret = email_api.unsupress_email(email_addr)
    assert ret
