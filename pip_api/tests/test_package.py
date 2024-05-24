"""
Test Requirement

"""
import pytest
from horey.pip_api.package import Package
from horey.pip_api.requirement import Requirement

# pylint: disable=missing-function-docstring


@pytest.mark.wip
def test_init():
    dict_src = {"name": "requests",
                 "version": "2.32.2"}
    obj = Package(dict_src)
    assert isinstance(obj, Package)


@pytest.mark.wip
def test_check_version_max_requirement():
    dict_src = {"name": "requests",
                 "version": "2.32.2"}
    package = Package(dict_src)

    requirement = Requirement("/test/requirements.txt", "requests==2.31.0")
    assert not package.check_version_max_requirement(requirement)
