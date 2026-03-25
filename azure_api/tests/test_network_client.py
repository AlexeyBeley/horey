"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""
from pathlib import Path

import pytest

from horey.azure_api.azure_api import AzureAPI
from horey.azure_api.azure_service_entities.route_table import RouteTable
from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.azure_api.azure_api_configuration_policy import AzureAPIConfigurationPolicy

mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_azure_api_mocks.py"
mock_values = CommonUtils.load_module(mock_values_file_path)

class Configuration(ConfigurationPolicy):
    """
    Tests configuration
    """

    TEST_CONFIG = None

    def __init__(self):
        super().__init__()
        self._network_client_resource_group_name = None
        self._azure_api_configuration_file_path = None
        self._location = None
        self._subscription = None
    @property
    def subscription(self):
        return self._subscription
    @subscription.setter
    def subscription(self, value):
        self._subscription = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def azure_api_configuration_file_path(self):
        return self._azure_api_configuration_file_path

    @azure_api_configuration_file_path.setter
    def azure_api_configuration_file_path(self, value):
        self._azure_api_configuration_file_path = value


    @property
    def network_client_resource_group_name(self):
        return self._network_client_resource_group_name

    @network_client_resource_group_name.setter
    def network_client_resource_group_name(self, value):
        self._network_client_resource_group_name = value


def init_configuration():
    ret = Configuration()
    ret.network_client_resource_group_name = mock_values.network_client_resource_group_name
    ret.azure_api_configuration_file_path = mock_values.azure_api_configuration_file_path
    ret.location = mock_values.location
    ret.subscription = mock_values.subscription
    return ret


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    Configuration.TEST_CONFIG = init_configuration()
    yield Configuration.TEST_CONFIG

@pytest.fixture(name="azure_api_configuration")
def fixture_azure_api_configuration():
    config = AzureAPIConfigurationPolicy()
    config.accounts_file = Configuration.TEST_CONFIG.azure_api_configuration_file_path
    config.azure_account = "test"
    config.azure_api_cache_dir = "/tmp/azure_api"
    yield config


@pytest.fixture(name="azure_api")
def fixture_azure_api(azure_api_configuration):
    azure_api = AzureAPI(configuration=azure_api_configuration)
    yield azure_api


@pytest.fixture(name="network_client")
def fixture_network_client(azure_api):
    yield azure_api.network_client


@pytest.mark.done
def test_get_all_virtual_machines():
    ret = network_client.get_all_nat_gateways(None, resource_group_name=mock_values["network_client_resource_group_name"])
    assert len(ret) > 0


@pytest.mark.done
def test_get_all_public_ip_addresses():
    ret = network_client.get_all_public_ip_addresses(None, resource_group_name=mock_values["network_client_resource_group_name"])
    assert len(ret) > 0


@pytest.mark.done
def test_get_all_network_interfaces():
    ret = network_client.get_all_network_interfaces(None, resource_group_name=mock_values["network_client_resource_group_name"])
    assert len(ret) > 0


@pytest.mark.unit
def test_get_all_route_tables(network_client):
    ret = network_client.get_all_route_tables(resource_group_name= Configuration.TEST_CONFIG.network_client_resource_group_name)
    assert len(ret) > 0

@pytest.mark.wip
def test_provision_route_table(network_client):
    route_table = RouteTable({})
    route_table.resource_group_name = Configuration.TEST_CONFIG.network_client_resource_group_name
    route_table.name = "test"
    route_table.disable_bgp_route_propagation = True
    route_table.subnets = []
    route_table.tags = {"name": route_table.name}
    route_table.location = Configuration.TEST_CONFIG.location
    route_table.routes = [{'id': f'/subscriptions/{Configuration.TEST_CONFIG.subscription}/resourceGroups/{Configuration.TEST_CONFIG.network_client_resource_group_name}/providers/Microsoft.Network/routeTables/manual/routes/8.8.8.8',
                           'name': '8.8.8.8',
                           'address_prefix': '8.8.8.8/32',
                           'next_hop_type': 'VirtualAppliance',
                           'next_hop_ip_address': '10.0.0.252',
                           'has_bgp_override': False}]
    assert network_client.provision_route_table(route_table)