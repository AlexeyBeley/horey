"""
Init and cache AWS objects.

"""
import shutil

import pytest

from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.cicd_api import CICDAPI, CICDAPIConfigurationPolicy
from horey.infrastructure_api.ec2_api import EC2API, EC2APIConfigurationPolicy

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from test_utils import init_from_secrets_api

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_cicd_mocks.py"
mock_values = CommonUtils.load_module(mock_values_file_path)


logger = get_logger()

aws_api: AWSAPI = AWSAPI()

class Configuration(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._crowdstrike_falcon_sensor_s3_directory_uri = None
        self._environment_api_configuration_file_secret_name = None
        self._ec2_api_configuration_file_secret_name = None
        self._hostname = None
        self._zabbix_server_address = None
        self._bastion_name = None

    @property
    def crowdstrike_falcon_sensor_s3_directory_uri(self):
        return self._crowdstrike_falcon_sensor_s3_directory_uri
    
    @crowdstrike_falcon_sensor_s3_directory_uri.setter
    def crowdstrike_falcon_sensor_s3_directory_uri(self, value):
        self._crowdstrike_falcon_sensor_s3_directory_uri = value

    @property
    def environment_api_configuration_file_secret_name(self):
        return self._environment_api_configuration_file_secret_name

    @environment_api_configuration_file_secret_name.setter
    def environment_api_configuration_file_secret_name(self, value: Path):
        self._environment_api_configuration_file_secret_name = value

    @property
    def ec2_api_configuration_file_secret_name(self):
        return self._ec2_api_configuration_file_secret_name

    @ec2_api_configuration_file_secret_name.setter
    def ec2_api_configuration_file_secret_name(self, value: Path):
        self._ec2_api_configuration_file_secret_name = value

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        self._hostname = value

    @property
    def zabbix_server_address(self):
        return self._zabbix_server_address

    @zabbix_server_address.setter
    def zabbix_server_address(self, value):
        self._zabbix_server_address = value

    @property
    def bastion_name(self):
        return self._bastion_name

    @bastion_name.setter
    def bastion_name(self, value):
        self._bastion_name = value


TEST_CONFIG = init_from_secrets_api(Configuration, mock_values.secret_name)

@pytest.fixture(name="env_api_integration")
def fixture_env_api_integration():
    breakpoint()
    env_configuration = init_from_secrets_api(EnvironmentAPIConfigurationPolicy, TEST_CONFIG.environment_api_configuration_file_secret_name)
    env_configuration.data_directory_path = Path("/tmp/test_data")
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    yield environment_api
    shutil.rmtree(env_configuration.data_directory_path)


@pytest.fixture(name="cicd_api_integration")
def fixture_cicd_api_integration(env_api_integration):
    cicd_api_configuration = CICDAPIConfigurationPolicy()
    cicd_api = CICDAPI(cicd_api_configuration, env_api_integration)
    yield cicd_api


@pytest.fixture(name="ec2_api_mgmt_integration")
def fixture_ec2_api_mgmt_integration(env_api_integration):
    api_configuration = EC2APIConfigurationPolicy()
    api = EC2API(api_configuration, env_api_integration)
    yield api


@pytest.mark.unit
def test_run_remote_provision_constructor_zabbix(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target, "zabbix", role="agent", 
                                                    zabbix_server_address=TEST_CONFIG.zabbix_server_address,
                                                    hostname=TEST_CONFIG.hostname)


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_provision_influxdb(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target,
                                                     "influxdb",
                                                     action="provision_influxdb"
                                                     )


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_enable_auth(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target,
                                                     "influxdb",
                                                     action="enable_auth",
                                                     admin_username="horey_admin",
                                                     admin_password="horey_admin_password")


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_create_databases(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb",
                                                     action="create_databases",
                                                     databases=["db_horey", "db_horey_kapacitor_alerts"],
                                                     admin_username="horey_admin",
                                                     admin_password="horey_admin_password"
                                                     )


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_create_user(cicd_api_integration, ec2_api_mgmt_integration):
    """

    :param cicd_api:
    :param ec2_api:
    :return:
    """

    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb",
                                                     action="create_user",
                                                     admin_username="horey_admin",
                                                     admin_password="horey_admin_password",
                                                     admin=True,
                                                     read_databases=["db_horey_kapacitor_alerts"],
                                                     write_databases=["db_horey_kapacitor_alerts"],
                                                     user="horey_kapacitor_user",
                                                     password="horey_kapacitor_password")


@pytest.mark.unit
def test_run_remote_provision_constructor_kapacitor_enable_auth(cicd_api_integration, ec2_api_mgmt_integration):
    """

    :param cicd_api:
    :param ec2_api:
    :return:
    """

    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb",
                                                     action="kapacitor_enable_auth",
                                                     admin_username="kapacitor_horey_admin",
                                                     admin_password="kapacitor_horey_admin_password"
                                                     )


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_provision_kapacitor(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb",
                                                     action="provision_kapacitor")


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_configure_kapacitor(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb",
                                                     action="configure_kapacitor",
                                                     username="horey_kapacitor_user",
                                                     password="horey_kapacitor_password")


@pytest.mark.todo
def test_run_remote_provision_constructor_influx_create_subscription(cicd_api_integration, ec2_api_mgmt_integration):

    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb", action="create_subscription", databases="db_horey", dst="http://127.0.0.1:9092")


@pytest.mark.wip
def test_run_remote_provision_constructor_crowdstrike_install_(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(TEST_CONFIG.hostname, bastion=ec2_instance)
    assert cicd_api_integration.run_remote_provision_constructor(target, "crowdstrike", action="install_falcon_sensor", s3_deployment_uri=TEST_CONFIG.crowdstrike_falcon_sensor_s3_directory_uri)
