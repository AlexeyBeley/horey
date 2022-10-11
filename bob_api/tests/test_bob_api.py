"""
Testing grafana API
"""
import os
import pytest

from horey.bob_api.bob_api import BobAPI
from horey.bob_api.bob_api_configuration_policy import BobAPIConfigurationPolicy
from horey.common_utils.common_utils import CommonUtils


ignore_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore")

configuration = BobAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(os.path.join(ignore_dir_path, "bob_api_configuration_values.py"))
configuration.init_from_file()

bob_api = BobAPI(configuration=configuration)

mock_values_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


# pylint: disable=missing-function-docstring

@pytest.mark.skip(reason="Can not test")
def test_init_bob_api():
    """
    Test Grafana API initiation
    @return:
    """
    _bob_api = BobAPI(configuration=configuration)
    assert isinstance(_bob_api, BobAPI)


@pytest.mark.skip(reason="Can not test")
def test_init_employees():
    """
    Dashboard folders initiation
    @return:
    """
    bob_api.init_employees(cache=True)


@pytest.mark.skip(reason="Can not test")
def test_get_reportees():
    """
    Dashboard folders initiation
    @return:
    """
    bob_api.init_employees(from_cache=True)
    ret = bob_api.get_reportees(mock_values["manager_display_name_2"])
    assert isinstance(ret, list)


@pytest.mark.skip(reason="Can not test")
def test_get_future_timeoffs():
    bob_api.get_future_timeoffs()


if __name__ == "__main__":
    #test_init_bob_api()
    #test_init_employees()
    #test_get_future_timeoffs()
    test_get_reportees()
