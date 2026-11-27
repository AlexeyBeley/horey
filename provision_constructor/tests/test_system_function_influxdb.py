"""
Test system_function_common module
"""
import shutil
from pathlib import Path

import pytest
import os
from horey.provision_constructor.system_functions.influxdb.provisioner import (
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
def test_generate_kapacitor_configuration_file(tmp_file_path):
    """
    def replace_regex_line(file_path, regex_pattern, replacement_line):

    :return:
    """

    provision_constructor = Provisioner("deployment_dir", False, False)
    shutil.copy2(Path(__file__).parent / "kapacitor.conf", tmp_file_path)

    assert provision_constructor.generate_kapacitor_configuration_file(tmp_file_path, username="user",
                                        password="pass",
                                        urls=["http://something:8086"])
    # Checks the reconfiguration
    assert provision_constructor.generate_kapacitor_configuration_file(tmp_file_path, username="user",
                                        password="pass",
                                        urls=["http://something:8086"])

    os.remove(tmp_file_path)
