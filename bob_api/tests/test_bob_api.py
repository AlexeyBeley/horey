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
    _bob_api = BobAPI(configuration=configuration)
    assert isinstance(_bob_api, BobAPI)


@pytest.mark.skip(reason="Can not test")
def test_init_employees():
    bob_api.init_employees()


@pytest.mark.skip(reason="Can not test")
def test_init_timeoff_requests():
    bob_api.init_timeoff_requests()


@pytest.mark.skip(reason="Can not test")
def test_get_reportees():
    bob_api.init_employees(from_cache=True)
    manager = CommonUtils.find_objects_by_values(bob_api.employees, {"display_name": mock_values["manager_display_name_2"]}, max_count=1)[0]
    ret = bob_api.get_reportees(manager)
    print(ret)
    assert isinstance(ret, list)


@pytest.mark.skip(reason="Can not test")
def test_get_future_timeoffs():
    ret = bob_api.get_future_timeoffs()
    assert isinstance(ret, dict)


@pytest.mark.skip(reason="Can not test")
def test_get_team_future_timeoffs():
    bob_api.init_employees(from_cache=True)
    manager = CommonUtils.find_objects_by_values(bob_api.employees, {"display_name": mock_values["manager_display_name_2"]}, max_count=1)[0]
    team_employees = bob_api.get_reportees(manager)
    ret = bob_api.get_future_timeoffs(employees=team_employees)
    assert isinstance(ret, dict)


@pytest.mark.skip(reason="Can not test")
def test_get_team_current_timeoffs():
    bob_api.init_employees(from_cache=True)
    manager = CommonUtils.find_objects_by_values(bob_api.employees, {"display_name": mock_values["my_manager_display_name"]}, max_count=1)[0]
    team_employees = bob_api.get_reportees(manager)

    ret = bob_api.get_current_timeoffs(employees=team_employees)
    print("TEAM VACATIONS!")
    print("TEAM VACATIONS!!")
    print("TEAM VACATIONS!!!")

    for _, vacations in ret.items():
        vacation = sorted(vacations, key=lambda vacation: vacation.date_end)[-1]
        print(vacation.generate_current_vacation_string())

    print("TEAM VACATIONS!!!")
    print("TEAM VACATIONS!!")
    print("TEAM VACATIONS!")

    assert isinstance(ret, dict)


@pytest.mark.skip(reason="Can not test")
def test_get_vacation_report():
    bob_api.init_employees(from_cache=True)
    bob_api.init_timeoff_requests()
    manager = CommonUtils.find_objects_by_values(bob_api.employees, {"display_name": mock_values["my_manager_display_name"]}, max_count=1)[0]
    ret = bob_api.get_vacation_report(manager)
    print(ret)


def test_print_employees_per_manager():
    bob_api.init_employees(from_cache=True)
    bob_api.print_employees_per_manager()


if __name__ == "__main__":
    #test_init_bob_api()
    #test_init_employees()
    #test_init_timeoff_requests()
    #test_get_future_timeoffs()
    #test_get_reportees()
    #test_get_team_future_timeoffs()
    #test_get_team_current_timeoffs()
    #test_print_employees_per_manager()
    test_get_vacation_report()
