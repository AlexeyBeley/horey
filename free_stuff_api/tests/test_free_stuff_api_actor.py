"""
Testing free_stuff_api_actor module.

"""
from pathlib import Path

import pytest
from horey.free_stuff_api.free_stuff_api_actor import update_component, run_server

free_stuff_api_config_file_path = Path(
    __file__).parent.parent.parent.parent / "ignore" / "test_frs_api_configuration.py"


@pytest.mark.unit
def test_update_component():
    class arguments:
        free_stuff_api_config_file_path = free_stuff_api_config_file_path

    update_component(arguments)


@pytest.mark.unit
def test_run_server():
    class arguments:
        free_stuff_api_config_file_path = free_stuff_api_config_file_path

    run_server(arguments)
