"""
Testing selenium api
"""
from pathlib import Path

import pytest
from horey.kijiji_api.kijiji_api import KijijiAPIConfigurationPolicy, KijijiAPI

config = KijijiAPIConfigurationPolicy()
config.configuration_file_full_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_kijiji_api_configuration.py"
config.init_from_file()



# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_get_free_items():
    kijiji_api = KijijiAPI(config)
    assert kijiji_api.get_free_items()
