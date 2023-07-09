"""
Testing chronograf api
"""
import os
import pytest

from horey.human_api.human_api import HumanAPI
from horey.human_api.user_story import UserStory
from horey.human_api.feature import Feature
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

    house_design = Feature()
    house_design.title = "Horey House Design"
    house_design.dod = "The house has backyard and front yard as in the pictures attached."

    front_yard = UserStory()
    front_yard.title = "Front yard design implementation"
    front_yard.priority = 1
    front_yard.dod = {
        1: "Looks like in the picture attached.",
        2: "It is clean of building garbage",
        3: "It is clean of yard waste"
    }
    house_design.add(front_yard)

    # region backyard
    backyard = UserStory()
    backyard.title = "Backyard design implementation"
    backyard.priority = 2
    backyard.dod = {
        1: "Looks like in the picture attached.",
        3: "Building garbage is collected",
        4: "Yard Waste is collected",
        5: "All tools are on their places"
    }
    house_design.add(backyard)
    # end_region

    front_yard_work = UserStory()
    front_yard_work.title = "Build the front yard"
    front_yard_work.priority = 1
    front_yard_work.dod = {
        1: "Looks like in the picture attached.",
        2: "Tree, bush, sprinkler, grass and gnomes",
        3: "Rocky pathway and fence"
    }
    front_yard.add(front_yard_work)


if __name__ == "__main__":
    # test_init_tasks_map()
    # test_daily_report()
    # test_daily_action()
    test_sprint_planning()

    test_daily_routine()
