"""
Testing github api functionality.

"""

import pytest
from pathlib import Path
from horey.github_api.actions.action import Action


@pytest.mark.unit
def test_init_from_file():
    assert Action()._init_from_file(Path(__file__).parent / "actions" / "action1.yaml")