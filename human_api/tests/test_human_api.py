"""
Testing chronograf api
"""
import os
import pytest

from horey.human_api.human_api import HumanAPI
from horey.human_api.human_api_configuration_policy import (
    HumanAPIConfigurationPolicy,
)

from horey.human_api.sprint import Sprint
from horey.common_utils.common_utils import CommonUtils

configuration = HumanAPIConfigurationPolicy()
ignore_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore"
    )
)

mock_values_file_path = os.path.join(ignore_dir, "human_api_mock_values.py")
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")

configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        ignore_dir,
        "human_api_configuration_values.py",
    )
)
configuration.init_from_file()
configuration.reports_dir_path = os.path.join(ignore_dir, "human_api")
configuration.sprint_name = mock_values["Sprint_name"]

human_api = HumanAPI(configuration=configuration)

# pylint: disable= missing-function-docstring


@pytest.mark.skip(reason="Can not test")
def test_daily_report():
    human_api.daily_report()


@pytest.mark.skip(reason="Can not test")
def test_daily_action():
    human_api.daily_action()


@pytest.mark.skip(reason="Can not test")
def test_init_tasks_map():
    human_api.init_tasks_map()


def test_daily_routine():
    human_api.daily_routine()


def test_sprint_planning():
    sprint = Sprint()
    sprint.name = "Test sprint"


if __name__ == "__main__":
    # test_init_tasks_map()
    # test_daily_report()
    # test_daily_action()
    test_sprint_planning()

    #test_daily_routine()
