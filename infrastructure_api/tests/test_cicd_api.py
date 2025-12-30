"""
Init and cache AWS objects.

"""
from pathlib import Path

import pytest
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.cicd_api import CICDAPI, CICDAPIConfigurationPolicy
from horey.infrastructure_api.ec2_api import EC2API, EC2APIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils
logger = get_logger()

aws_api = AWSAPI()

ignore_directory = Path(__file__).parent.parent.parent.parent / "ignore" / "infrastructure_api"
ignore = CommonUtils.load_module(ignore_directory / "test_cicd_api_mock.py")

# pylint: disable= missing-function-docstring


@pytest.fixture(name="cicd_api")
def fixture_cicd_api():
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.configuration_file_full_path = ignore_directory / "environment_dev.py"
    env_configuration.init_from_file()
    #env_configuration.project_name = "hry"
    #env_configuration.project_name_abbr = "hry"
    #env_configuration.environment_level = "development"
    #env_configuration.environment_name = "test"
    #env_configuration.region = "us-west-2"
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    cicd_api_configuration = CICDAPIConfigurationPolicy()
    cicd_api = CICDAPI(cicd_api_configuration, environment_api)

    yield cicd_api


@pytest.fixture(name="ec2_api")
def fixture_ec2_api():
    env_configuration = EnvironmentAPIConfigurationPolicy()
    env_configuration.configuration_file_full_path = ignore_directory / "environment_dev_bastion.py"
    env_configuration.init_from_file()
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    api_configuration = EC2APIConfigurationPolicy()
    api = EC2API(api_configuration, environment_api)
    yield api


@pytest.mark.unit
def test_run_remote_provision_constructor_zabbix(cicd_api, ec2_api):
    ec2_instance = ec2_api.get_instance(name=ignore.bastion_name)
    target = cicd_api.generate_deployment_target(ignore.hostname, bastion=ec2_instance)
    assert cicd_api.run_remote_provision_constructor(target, "zabbix", role="agent", 
                                                    zabbix_server_address=ignore.zabbix_server_address,
                                                    hostname=ignore.hostname)


@pytest.mark.wip
def test_run_remote_provision_constructor_influx_provision_influxdb(cicd_api, ec2_api):
    ec2_instance = ec2_api.get_instance(name=ignore.bastion_name)
    target = cicd_api.generate_deployment_target(ignore.hostname, bastion=ec2_instance)
    assert cicd_api.run_remote_provision_constructor(target,
                                                     "influxdb",
                                                     action="provision_influxdb",
                                                     admin_username="horey_admin",
                                                     admin_password="horey_admin_password")


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_create_databases(cicd_api, ec2_api):
    ec2_instance = ec2_api.get_instance(name=ignore.bastion_name)
    target = cicd_api.generate_deployment_target(ignore.hostname, bastion=ec2_instance)
    assert cicd_api.run_remote_provision_constructor(target, "influxdb", action="create_databases", databases=["db_horey", "db_horey_kapacitor_alerts"],)


@pytest.mark.todo
def test_run_remote_provision_constructor_influx_create_user(cicd_api, ec2_api):
    """

    :param cicd_api:
    :param ec2_api:
    :return:
    """
    ec2_instance = ec2_api.get_instance(name=ignore.bastion_name)
    target = cicd_api.generate_deployment_target(ignore.hostname, bastion=ec2_instance)
    assert cicd_api.run_remote_provision_constructor(target, "influxdb",
                                                     action="create_user",
                                                     databases=["db_horey_kapacitor_alerts"],
                                                     user="horey_kapacitor_user",
                                                     password="horey_kapacitor_password")


@pytest.mark.todo
def test_run_remote_provision_constructor_influx_provision_kapacitor(cicd_api, ec2_api):
    ec2_instance = ec2_api.get_instance(name=ignore.bastion_name)
    target = cicd_api.generate_deployment_target(ignore.hostname, bastion=ec2_instance)
    assert cicd_api.run_remote_provision_constructor(target, "influxdb", action="provision_kapacitor", influx_username="horey_kapacitor_user", influx_password="horey_kapacitor_password")


@pytest.mark.todo
def test_run_remote_provision_constructor_influx_create_subscription(cicd_api, ec2_api):

    ec2_instance = ec2_api.get_instance(name=ignore.bastion_name)
    target = cicd_api.generate_deployment_target(ignore.hostname, bastion=ec2_instance)
    assert cicd_api.run_remote_provision_constructor(target, "influxdb", action="create_subscription", databases="db_horey", dst="http://127.0.0.1:9092")

