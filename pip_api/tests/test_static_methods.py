"""
Static method tests

"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "horey", "pip_api")))

from static_methods import StaticMethods


# pylint: disable= missing-function-docstring

@pytest.mark.todo
def test_init():
    assert StaticMethods.execute
