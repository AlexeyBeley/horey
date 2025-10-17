"""
Testing selenium api
"""

import pytest
from pathlib import Path
from horey.selenium_api.fb import FB
from horey.selenium_api.fb_configuration_policy import FBConfigurationPolicy

config = FBConfigurationPolicy()
config.configuration_file_full_path = Path(__file__).parent.parent.parent.parent / "ignore" / "fb" / "fb_configuration.py"
config.init_from_file()
fb = FB(config)


# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_load_free():
    assert fb.load_free()
