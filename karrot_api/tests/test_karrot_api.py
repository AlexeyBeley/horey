"""
Testing selenium api
"""
from pathlib import Path

import pytest
from horey.karrot_api.karrot_api import KarrotAPIConfigurationPolicy, KarrotAPI

config = KarrotAPIConfigurationPolicy()
config.configuration_file_full_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_fb_api_configuration.py"
config.init_from_file()



# pylint: disable= missing-function-docstring


@pytest.mark.unit
def test_get_free_items():
    karrot_api = KarrotAPI(config)
    assert karrot_api.get_free_items()
