"""
Testing chronograf api
"""
import datetime
import os
import pytest

from horey.human_api.human_api import HumanAPI
from horey.human_api.human_api_configuration_policy import (
    HumanAPIConfigurationPolicy,
)
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
daily_hapi_file_path = os.path.join(ignore_dir, "human_api", "daily_"+str(datetime.date.today())+".hapi")
protected_output_file_path = daily_hapi_file_path.replace(".hapi", "_input.hapi")
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        ignore_dir,
        "human_api_configuration_values.py",
    )
)
configuration.init_from_file()

human_api = HumanAPI(configuration=configuration)

# pylint: disable= missing-function-docstring


@pytest.mark.skip(reason="Can not test")
def test_daily_report():
    if os.path.exists(protected_output_file_path):
        return
    human_api.daily_report(daily_hapi_file_path, protected_output_file_path, sprint_name=mock_values["Sprint_name"])


@pytest.mark.skip(reason="Can not test")
def test_daily_action():
    human_api.daily_action(protected_output_file_path, mock_values["Sprint_name"])


@pytest.mark.skip(reason="Can not test")
def test_init_tasks_map():
    human_api.init_tasks_map()


if __name__ == "__main__":
    # test_init_tasks_map()
    test_daily_report()
    breakpoint()
    test_daily_action()
