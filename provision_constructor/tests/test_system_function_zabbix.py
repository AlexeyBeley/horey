"""
Test system_function_common module
"""
import shutil
from pathlib import Path

import pytest
import os
from horey.provision_constructor.system_functions.zabbix.provisioner import (
    Provisioner
)

# pylint: disable = missing-function-docstring
DEPLOYMENT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "provision_constructor_deployment"
)

@pytest.fixture(name="tmp_file_path")
def tmp_file_path_fixture():
    file_path = Path("/tmp/file.txt")
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass

    yield file_path

    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


@pytest.mark.unit
def test_provision_agent():
    provision_constructor = Provisioner(role="agent",
                                        zabbix_server_address="horey_zabbix_server_address",
                                        hostname="this-server")
    assert provision_constructor._provision()


@pytest.mark.unit
def test_generate_configuration_file(tmp_file_path):
    """
    def replace_regex_line(file_path, regex_pattern, replacement_line):

    :return:
    """

    provision_constructor = Provisioner(False, False, role="agent",
                                        zabbix_server_address="horey_zabbix_server_address",
                                        hostname="this-server")
    shutil.copy2(Path(__file__).parent / "zabbix_agent2.conf", tmp_file_path)

    assert provision_constructor.generate_configuration_file(tmp_file_path)
    # Checks the reconfiguration
    assert provision_constructor.generate_configuration_file(tmp_file_path)

    os.remove(tmp_file_path)
