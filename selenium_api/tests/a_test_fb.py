"""
Testing selenium api
"""
breakpoint()
import pytest

from horey.selenium_api import SeleniumAPI


api = SeleniumAPI()


# pylint: disable= missing-function-docstring


@pytest.mark.wip
def test_connect():
    assert api.connect()
