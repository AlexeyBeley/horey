"""
Testing github api functionality.

"""

import pytest
from pathlib import Path
from horey.github_api.actions.workflow import Workflow


@pytest.mark.unit
def test_init_from_file():
    assert Workflow().init_from_file(Path(__file__).parent / "workflows" / "workflow1.yaml")