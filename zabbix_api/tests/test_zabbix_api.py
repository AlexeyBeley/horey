import pytest
import os

from horey.zabbix_api.zabbix_api import ZabbixAPI
from horey.zabbix_api.zabbix_api_configuration_policy import (
    ZabbixAPIConfigurationPolicy,
)
from horey.h_logger import get_logger

configuration_values_file_full_path = None
logger = get_logger()

configuration = ZabbixAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "zabbix_api_configuration_values.py",
    )
)
configuration.init_from_file()

zabbix_api = ZabbixAPI(configuration=configuration)


# region done
@pytest.mark.unit
def test_init_hosts():
    zabbix_api.init_hosts()
    logger.info(f"len(hosts) = {len(zabbix_api.hosts)}")
    assert isinstance(zabbix_api.hosts, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_init_templates():
    zabbix_api.init_templates()
    logger.info(f"len(templates) = {len(zabbix_api.templates)}")
    assert isinstance(zabbix_api.templates, list)


@pytest.mark.skip(reason="IAM policies will be inited explicitly")
def test_provision_host():
    zabbix_api.init_hosts()
    for host in zabbix_api.hosts:
        if "template" == host.name:
            break

    host.name = "alexeytest"
    host.host = host.name

    zabbix_api.provision_host(host)

    logger.info(f"len(hosts) = {len(zabbix_api.hosts)}")
    assert isinstance(zabbix_api.hosts, list)


@pytest.mark.unit
def test_delte_hosts():
    zabbix_api.init_hosts()
    logger.info(f"len(hosts) = {len(zabbix_api.hosts)}")
    for zabbix_host in zabbix_api.hosts:
        if "horey" in zabbix_host.host:
            assert zabbix_api.delete_host(zabbix_host)
