"""
Static method tests

"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "horey", "pip_api")))

from standalone_methods import StandaloneMethods


# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init():
    assert StandaloneMethods.execute
