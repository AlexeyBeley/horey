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
daily_hapi_file_path = os.path.join(ignore_dir, "human_api", "daily_"+str(datetime.date.today())+".hapi")
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
    lst_ret = human_api.daily_report(daily_hapi_file_path)


@pytest.mark.skip(reason="Can not test")
def test_daily_action():
    lst_ret = human_api.daily_action(daily_hapi_file_path)


@pytest.mark.skip(reason="Can not test")
def test_init_tasks_map():
    lst_ret = human_api.init_tasks_map()
    assert len(lst_ret) > 0


if __name__ == "__main__":
    #test_init_tasks_map()
    test_daily_report()
    test_daily_action()

