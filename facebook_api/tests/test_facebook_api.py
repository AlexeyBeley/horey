"""
Testing selenium api
"""
from pathlib import Path

import pytest
from horey.facebook_api.facebook_api import FacebookAPIConfigurationPolicy, FacebookAPI

config = FacebookAPIConfigurationPolicy()
config.configuration_file_full_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_fb_api_configuration.py"
config.init_from_file()



# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_load_free():
    facebook_api = FacebookAPI(config)
    assert facebook_api.load_free()
