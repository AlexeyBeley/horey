"""
test cicd

"""
import shutil

import sys
from pathlib import Path

import pytest
import requests

sys.path.append(str(Path(__file__).parent))
from test_utils import init_from_secrets_api
from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.aws_api.aws_api import AWSAPI
from horey.h_logger import get_logger
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.cicd_api import CICDAPI, CICDAPIConfigurationPolicy
from horey.infrastructure_api.ec2_api import EC2API, EC2APIConfigurationPolicy
from horey.github_api.github_api import GithubAPI, GithubAPIConfigurationPolicy

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_cicd_mocks.py"
mock_values = CommonUtils.load_module(mock_values_file_path)

# pylint: disable = missing-function-docstring
logger = get_logger()

aws_api: AWSAPI = AWSAPI()


class Configuration(ConfigurationPolicy):
    """
    Tests configuration
    """

    TEST_CONFIG = None

    def __init__(self):
        super().__init__()
        self._crowdstrike_falcon_sensor_s3_directory_uri = None
        self._environment_api_configuration_file_secret_name = None
        self._ec2_api_configuration_file_secret_name = None
        self._hostname = None
        self._zabbix_server_address = None
        self._bastion_name = None
        self._environment_api_mgmt_configuration_file_secret_name = None
        self._crowdstrike_falcon_sensor_cid = None
        self._bastion_chain = None
        self._windows_ssh_key = None
        self._windows_hostname = None
        self._ec2_vrrp_master = None
        self._ec2_vrrp_backup = None
        self._github_api_configuration_file_secret_name = None
        self._github_hagent_runner_name = None
        self._github_hagent_repo_name = None

    @property
    def github_hagent_runner_name(self):
        return self._github_hagent_runner_name

    @github_hagent_runner_name.setter
    def github_hagent_runner_name(self, value):
        self._github_hagent_runner_name = value

    @property
    def github_hagent_repo_name(self):
        return self._github_hagent_repo_name
    @github_hagent_repo_name.setter
    def github_hagent_repo_name(self, value):
        self._github_hagent_repo_name = value
        self._github_hagent_runner_name = None

    @property
    def github_api_configuration_file_secret_name(self):
        return self._github_api_configuration_file_secret_name

    @github_api_configuration_file_secret_name.setter
    def github_api_configuration_file_secret_name(self, value):
        self._github_api_configuration_file_secret_name = value
        self._github_api_configuration_file_secret_name = None

    @property
    def ec2_vrrp_master(self):
        return self._ec2_vrrp_master

    @ec2_vrrp_master.setter
    def ec2_vrrp_master(self, value):
        self._ec2_vrrp_master = value

    @property
    def ec2_vrrp_backup(self):
        return self._ec2_vrrp_backup

    @ec2_vrrp_backup.setter
    def ec2_vrrp_backup(self, value):
        self._ec2_vrrp_backup = value

    @property
    def bastion_chain(self):
        return self._bastion_chain

    @bastion_chain.setter
    def bastion_chain(self, value):
        self._bastion_chain = value

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

    @property
    def environment_api_mgmt_configuration_file_secret_name(self):
        return self._environment_api_mgmt_configuration_file_secret_name

    @environment_api_mgmt_configuration_file_secret_name.setter
    def environment_api_mgmt_configuration_file_secret_name(self, value):
        self._environment_api_mgmt_configuration_file_secret_name = value

    @property
    def crowdstrike_falcon_sensor_cid(self):
        return self._crowdstrike_falcon_sensor_cid

    @crowdstrike_falcon_sensor_cid.setter
    def crowdstrike_falcon_sensor_cid(self, value):
        self._crowdstrike_falcon_sensor_cid = value

    @property
    def windows_ssh_key(self):
        return self._windows_ssh_key

    @windows_ssh_key.setter
    def windows_ssh_key(self, value):
        self._windows_ssh_key = value

    @property
    def windows_hostname(self):
        return self._windows_hostname

    @windows_hostname.setter
    def windows_hostname(self, value):
        self._windows_hostname = value


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    Configuration.TEST_CONFIG = init_from_secrets_api(Configuration, mock_values.secret_name)
    yield Configuration.TEST_CONFIG


@pytest.fixture(name="env_api_integration")
def fixture_env_api_integration():
    env_configuration = init_from_secrets_api(EnvironmentAPIConfigurationPolicy,
                                              Configuration.TEST_CONFIG.environment_api_configuration_file_secret_name)
    if isinstance(env_configuration.private_subnets, str):
        env_configuration.private_subnets = env_configuration.private_subnets.split(",")
    if isinstance(env_configuration.public_subnets, str):
        env_configuration.public_subnets = env_configuration.public_subnets.split(",")
    env_configuration.data_directory_path = Path("/tmp/test_data")
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    yield environment_api
    if env_configuration.data_directory_path.exists():
        shutil.rmtree(env_configuration.data_directory_path)


@pytest.fixture(name="env_api_mgmt_integration")
def fixture_env_api_mgmt_integration():
    env_configuration = init_from_secrets_api(EnvironmentAPIConfigurationPolicy,
                                              Configuration.TEST_CONFIG.environment_api_mgmt_configuration_file_secret_name)
    env_configuration.data_directory_path = Path("/tmp/test_data")
    infrastructure_api = InfrastructureAPI()
    environment_api = infrastructure_api.get_environment_api(env_configuration, aws_api=aws_api)
    yield environment_api
    if env_configuration.data_directory_path.exists():
        shutil.rmtree(env_configuration.data_directory_path)


@pytest.fixture(name="cicd_api_integration")
def fixture_cicd_api_integration(env_api_integration):
    cicd_api_configuration = CICDAPIConfigurationPolicy()
    cicd_api = CICDAPI(cicd_api_configuration, env_api_integration)

    cicd_api.jenkins_master_ecs_api.build_api.git_api.configuration.git_directory_path = Path(__file__).parent.parent.parent.parent
    yield cicd_api


@pytest.fixture(name="ec2_api_mgmt_integration")
def fixture_ec2_api_mgmt_integration(env_api_mgmt_integration):
    api_configuration = EC2APIConfigurationPolicy()
    api = EC2API(api_configuration, env_api_mgmt_integration)
    yield api


@pytest.fixture(name="github_api")
def fixture_github_api():
    github_config = init_from_secrets_api(GithubAPIConfigurationPolicy,
                                              Configuration.TEST_CONFIG.github_api_configuration_file_secret_name)
    github_api = GithubAPI(github_config)
    yield github_api


@pytest.mark.unit
def test_run_remote_provision_constructor_zabbix(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
    assert cicd_api_integration.run_remote_provision_constructor(target, "zabbix",
                                                                 role="agent",
                                                                 zabbix_server_address="horey.zabbix.server",
                                                                 hostname=Configuration.TEST_CONFIG.hostname)


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_provision_influxdb(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
    assert cicd_api_integration.run_remote_provision_constructor(target,
                                                                 "influxdb",
                                                                 action="provision_influxdb"
                                                                 )


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_enable_auth(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
    assert cicd_api_integration.run_remote_provision_constructor(target,
                                                                 "influxdb",
                                                                 action="enable_auth",
                                                                 admin_username="horey_admin",
                                                                 admin_password="horey_admin_password")


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_create_databases(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
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

    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
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

    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb",
                                                                 action="kapacitor_enable_auth",
                                                                 admin_username="kapacitor_horey_admin",
                                                                 admin_password="kapacitor_horey_admin_password"
                                                                 )


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_provision_kapacitor(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb",
                                                                 action="provision_kapacitor")


@pytest.mark.unit
def test_run_remote_provision_constructor_influx_configure_kapacitor(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb",
                                                                 action="configure_kapacitor",
                                                                 username="horey_kapacitor_user",
                                                                 password="horey_kapacitor_password")


@pytest.mark.todo
def test_run_remote_provision_constructor_influx_create_subscription(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    target = cicd_api_integration.generate_deployment_target(Configuration.TEST_CONFIG.hostname,
                                                             bastions=[ec2_instance])
    assert cicd_api_integration.run_remote_provision_constructor(target, "influxdb", action="create_subscription",
                                                                 databases="db_horey", dst="http://127.0.0.1:9092")


@pytest.mark.unit
def test_run_remote_provision_constructor_crowdstrike_install_(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=[ec2_instance])
    for target in targets:
        assert cicd_api_integration.run_remote_provision_constructor(target,
                                                                     "crowdstrike",
                                                                     action="install_falcon_sensor",
                                                                     s3_deployment_uri=Configuration.TEST_CONFIG.crowdstrike_falcon_sensor_s3_directory_uri,
                                                                     falcon_sensor_cid=Configuration.TEST_CONFIG.crowdstrike_falcon_sensor_cid)


@pytest.mark.unit
def test_run_remote_provision_constructor_mysql_client(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=[ec2_instance])
    for target in targets:
        assert cicd_api_integration.run_remote_provision_constructor(target,
                                                                     "apt_package_generic",
                                                                     package_names=["mysql-client", "redis-tools",
                                                                                    "postgresql-client"])


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instance = ec2_api_mgmt_integration.get_instance(name=Configuration.TEST_CONFIG.bastion_name)
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=[ec2_instance])

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "copy_generic",
                                                              src=Path(__file__),
                                                              dst=Path("/tmp") / Path(__file__).name,
                                                              sudo=True)

    for target in targets:
        target.append_remote_step("CopyTest", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_restart(cicd_api_integration):
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.bastion_name)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "systemd",
                                                              action="restart_service",
                                                              service_name="cron")

    for target in targets:
        target.append_remote_step("RestartServiceTest", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_bastion_chain(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "copy_generic",
                                                              src=Path(__file__),
                                                              dst=Path("/tmp") / Path(__file__).name,
                                                              sudo=True)

    for target in targets:
        target.append_remote_step("CopyTest", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_raw(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "raw",
                                                              command="sudo apt update")

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_raw(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "horey_package_generic",
                                                              package_name="provision_constructor",
                                                              local_horey_repo_path=Path(__file__).parent.parent.parent)

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_logstash_install(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances
                                                               )

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "logstash",
                                                              action="install",
                                                              run_as_root=True
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_logstash_install_plugin(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "logstash",
                                                              action="install_plugin",
                                                              plugin_name="logstash-output-opensearch")

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_dns_set_dns_resolvers(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "dns",
                                                              action="set_dns_resolvers",
                                                              primary=["1.1.1.1", "8.8.8.8"],
                                                              fallback=["9.9.9.9", "208.67.222.222"])

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_set_ntp_server(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "ntp",
                                                              action="set_ntp_server"
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_copy_generic_dir(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "copy_generic",
                                                              src=Path(__file__).parent,
                                                              dst=Path("/etc/logstash"),
                                                              sudo=True
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_logstash_restart(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "logstash",
                                                              action="restart"
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_docker_install(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "docker"
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_swap(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "swap"
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_horey_package_generic_venv(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "horey_package_generic",
                                                              package_names=["aws_api",
                                                                             "docker_api",
                                                                             "h_logger",
                                                                             "configuration_policy",
                                                                             "common_utils"],
                                                              horey_repo_path=Path("/opt/horey"),
                                                              local_horey_repo_path=Path(__file__).parent.parent.parent)

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_zabbix_agent(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        zabbix_agent_version = "zabbix-release_7.0-2+ubuntu24.04_all.deb"
        url = f"https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/{zabbix_agent_version}"

        response = requests.get(url)

        agent2_deb_path = target.local_deployment_dir_path / "zabbix_agent.deb"
        if response.status_code == 200:
            with open(agent2_deb_path, "wb") as f:
                f.write(response.content)
        else:
            raise Exception(f"Failed to download file. Status code: {response.status_code}")

        cicd_api_integration.run_remote_provision_constructor(target, "zabbix",
                                                              role="agent",
                                                              zabbix_server_address="zabbix.horey.sever",
                                                              hostname=Configuration.TEST_CONFIG.hostname,
                                                              deb_file_path=Path(agent2_deb_path))

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_docker_prune_old_images(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "raw",
                                                              command="sudo rm -rf /opt/horey &&"
                                                                      " sudo mkdir /opt/horey &&"
                                                                      " sudo chown -R ubuntu:ubuntu /opt/horey"
                                                              )

        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "horey_package_generic",
                                                              package_names=[
                                                                  "docker_api",
                                                                  "infrastructure_api"
                                                              ],
                                                              horey_repo_path=Path("/opt/horey"),
                                                              local_horey_repo_path=Path(__file__).parent.parent.parent)

        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "docker",
                                                              action="prune_old_images",
                                                              horey_dir_path="/opt/horey",
                                                              limit=4
                                                              )

        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "docker",
                                                              action="pull",
                                                              horey_dir_path="/opt/horey",
                                                              image="public.ecr.aws/lambda/python:3.12"
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_docker_login(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "docker",
                                                              action="login",
                                                              region="us-west-2",
                                                              logout=True,
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_hardening(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "hardening",
                                                              action="harden",
                                                              )

    for target in targets:
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_windows_target_raw(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    targets = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.windows_hostname,
                                                               bastions=ec2_instances)

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "raw",
                                                              command="dir",
                                                              windows=True
                                                              )

    for target in targets:
        target.deployment_target_user_name = "Administrator"
        target.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets(targets, asynchronous=False)


@pytest.mark.unit
def test_provision_jenkins_master_infrastructure(cicd_api_integration, ec2_api_mgmt_integration):
    assert cicd_api_integration.provision_jenkins_master_infrastructure()

@pytest.mark.unit
def test_update_jenkins_master(cicd_api_integration):
    assert cicd_api_integration.update_jenkins_master()

@pytest.mark.unit
def test_provision_jenkins_hagent_infrastructure(cicd_api_integration, ec2_api_mgmt_integration):
    assert cicd_api_integration.provision_jenkins_hagent_infrastructure()


@pytest.mark.unit
def test_update_hagent(cicd_api_integration, ec2_api_mgmt_integration):
    cicd_api_integration.ecs_api.get_next_build_number = lambda : 1
    assert cicd_api_integration.update_hagent()


@pytest.mark.unit
def test_provision_github_hagent(cicd_api_integration, ec2_api_mgmt_integration, github_api):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    assert cicd_api_integration.provision_github_hagent(github_api,
                                                        bastions=ec2_instances,
                                                        repository_name=Configuration.TEST_CONFIG.github_hagent_repo_name
                                                        )

@pytest.mark.unit
def test_provision_github_hagent_dockerized(cicd_api_integration, ec2_api_mgmt_integration, github_api):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]
    assert cicd_api_integration.provision_github_hagent_dockerized(github_api,
                                                        bastions=ec2_instances,
                                                        repository_name=Configuration.TEST_CONFIG.github_hagent_repo_name,
                                                        horey_repo_path = Path(__file__).parent.parent.parent
                                                        )

@pytest.mark.unit
@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_vrrp_install(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]

    target_master = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.ec2_vrrp_master,
                                                                     bastions=ec2_instances
                                                                     )[0]

    target_backup = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.ec2_vrrp_backup,
                                                                     bastions=ec2_instances
                                                                     )[0]
    virtual_ip_address = ".".join(target_backup.deployment_target_address.split(".")[:3]) + ".253"

    # master
    def entrypoint_1():
        cicd_api_integration.run_remote_provision_constructor(target_master,
                                                              "vrrp",
                                                              action="install",
                                                              virtual_ip_address=virtual_ip_address,
                                                              master=target_master.deployment_target_address,
                                                              backups=[target_backup.deployment_target_address]
                                                              )

    target_master.append_remote_step("Test", entrypoint_1)

    def entrypoint_2():
        cicd_api_integration.run_remote_provision_constructor(target_backup,
                                                              "vrrp",
                                                              action="install",
                                                              virtual_ip_address=virtual_ip_address,
                                                              master=target_master.deployment_target_address,
                                                              backups=[target_backup.deployment_target_address]
                                                              )

    target_master.append_remote_step("Test", entrypoint_2)
    assert cicd_api_integration.run_remote_deployer_deploy_targets([target_backup], asynchronous=False)
    assert cicd_api_integration.run_remote_deployer_deploy_targets([target_master, target_backup], asynchronous=False)



@pytest.mark.todo
def test_run_remote_deployer_deploy_targets_vrrp_install(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]

    target_master = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.ec2_vrrp_master,
                                                                     bastions=ec2_instances
                                                                     )[0]

    target_backup = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.ec2_vrrp_backup,
                                                                     bastions=ec2_instances
                                                                     )[0]
    virtual_ip_address1 = ".".join(target_backup.deployment_target_address.split(".")[:3]) + ".253"
    virtual_ip_address2 = ".".join(target_backup.deployment_target_address.split(".")[:3]) + ".252"

    # master
    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target_master,
                                                              "vrrp",
                                                              action="install",
                                                              architechture="active_active",
                                                              address_map={
                                                                  virtual_ip_address1: target_master.deployment_target_address,
                                                                  virtual_ip_address2: target_backup.deployment_target_address},
                                                              )

    target_master.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets([target_master], asynchronous=False)



@pytest.mark.wip
def test_run_remote_deployer_deploy_targets_nat_install(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]

    target_master = cicd_api_integration.generate_deployment_targets(Configuration.TEST_CONFIG.ec2_vrrp_master,
                                                                     bastions=ec2_instances
                                                                     )[0]

    def entrypoint():
        cicd_api_integration.run_remote_provision_constructor(target_master,
                                                              "nat",
                                                              action="install",
                                                              src_network=target_master.deployment_target_address
                                                              )

    target_master.append_remote_step("Test", entrypoint)
    assert cicd_api_integration.run_remote_deployer_deploy_targets([target_master], asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_disk_install(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]

    target = cicd_api_integration.generate_deployment_targets("test-instance",
                                                              bastions=ec2_instances
                                                              )[0]

    # master
    def entrypoint():
        blockdevices = cicd_api_integration.run_remote_provision_constructor(target,
                                                                             "disk",
                                                                             action="get_blockdevices",
                                                                             )
        for blockdevice in blockdevices:
            if blockdevice["size"] == "98G":
                break
        else:
            raise ValueError("Was not able to find block device")

        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "disk",
                                                              action="format",
                                                              blockdevice=blockdevice,
                                                              force=True
                                                              )
        blockdevices = cicd_api_integration.run_remote_provision_constructor(target,
                                                                             "disk",
                                                                             action="get_blockdevices",
                                                                             blockdevice=blockdevice
                                                                             )
        blockdevice =  blockdevices[0]
        if len(blockdevice["children"]) != 1:
            raise ValueError("Wrong number of children")
        child = blockdevice["children"][0]

        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "disk",
                                                              action="mount",
                                                              src=Path(child["path"]),
                                                              dst=Path("/var/lib/my_mount"),
                                                              chmod="710"
                                                              )

    target.append_remote_step("Test", entrypoint)
    # backup

    assert cicd_api_integration.run_remote_deployer_deploy_targets([target], asynchronous=False)


@pytest.mark.unit
def test_run_remote_deployer_deploy_targets_disk_partition(cicd_api_integration, ec2_api_mgmt_integration):
    ec2_instances = [ec2_api_mgmt_integration.get_instance(name=ec2_name) for ec2_name in
                     Configuration.TEST_CONFIG.bastion_chain.split(",")]

    target = cicd_api_integration.generate_deployment_targets("test-instance",
                                                              bastions=ec2_instances
                                                              )[0]

    # master
    def entrypoint():
        blockdevices = cicd_api_integration.run_remote_provision_constructor(target,
                                                                             "disk",
                                                                             action="get_blockdevices",
                                                                             )
        for blockdevice in blockdevices:
            if blockdevice["size"] == "68G":
                break
        else:
            raise ValueError("Was not able to find block device")

        cicd_api_integration.run_remote_provision_constructor(target,
                                                              "disk",
                                                              action="partition",
                                                              blockdevice=blockdevice,
                                                              parts=[("linux-swap", "1MiB", "32GB"),
                                                                     ("ext4", "32GB", "52GB"),
                                                                     ("ext4", "52GB", "100%")],
                                                              force=True
                                                              )
        blockdevices = cicd_api_integration.run_remote_provision_constructor(target,
                                                                             "disk",
                                                                             action="get_blockdevices",
                                                                             blockdevice=blockdevice)
        blockdevice = blockdevices[0]
        assert blockdevice


    target.append_remote_step("Test", entrypoint)
    # backup

    assert cicd_api_integration.run_remote_deployer_deploy_targets([target], asynchronous=False)

