"""
Testing chronograf api
"""
import os

from horey.human_api.human_api import HumanAPI
from horey.human_api.user_story import UserStory
from horey.human_api.task import Task
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

# pylint: disable= too-many-statements
def test_sprint_planning():
    sprint = Sprint()
    sprint.name = "Test sprint"

    feature_sms = Feature()
    feature_sms.title = "Sprint Management system"
    feature_sms.priority = 1
    feature_sms.dod = {1: "Sprint retrospective logs current time spent",
                        2: "Sprint retrospective resets tasks' times.",
                        3: "Creates work plan - user stories tasks and bugs"}

    sprint_retrospective = UserStory()
    sprint_retrospective.title = "Sprint retrospective"
    sprint_retrospective.priority = 1
    sprint_retrospective.dod = {
        1: "Current status is saved in json format in a local file",
        2: "Current status is saved in json format as a comment in each task.",
        4: "All spent time is reset to 0"
    }
    feature_sms.add(sprint_retrospective)

    sprint_retrospective_collect_data = UserStory()
    sprint_retrospective_collect_data.title = "Generate Sprint status"
    sprint_retrospective_collect_data.priority = 1
    sprint_retrospective_collect_data.dod = {
        1: "Fetch NEW, ACTIVE, BLOCKED and CLOSED tasks, bugs and user_stories assigned to this sprint",
        2: "Fetch Assumed time and Reported working time",
        3: "Fetch parents_ids and children_ids relations",
        4: "Return List with all collected data"
    }
    sprint_retrospective.add(sprint_retrospective_collect_data)

    fetch_sprint_items = Task()
    fetch_sprint_items.title = "Fetch Sprint items"
    fetch_sprint_items.priority = 1
    fetch_sprint_items.time_estimation = 4
    fetch_sprint_items.dod = {
        1: "Fetch NEW, ACTIVE, BLOCKED and CLOSED tasks, bugs and user_stories assigned to this sprint",
        2: "Input sprint ID",
        3: "Output List of items with"
    }
    sprint_retrospective_collect_data.add(fetch_sprint_items)

    fetch_sprint_owners = Task()
    fetch_sprint_owners.title = "Fetch Sprint owners"
    fetch_sprint_owners.priority = 2
    fetch_sprint_owners.time_estimation = 2
    fetch_sprint_owners.dod = {
        1: "Fetch item owners",
        2: "Input sprint ID",
        3: "Output List of items with owners"
    }
    sprint_retrospective_collect_data.add(fetch_sprint_owners)

    fetch_sprint_times = Task()
    fetch_sprint_times.title = "Fetch Sprint times"
    fetch_sprint_times.priority = 2
    fetch_sprint_times.time_estimation = 2
    fetch_sprint_times.dod = {
        1: "Fetch Assumed time and Reported working time",
        2: "Input sprint ID",
        3: "Output List of items with times"
    }
    sprint_retrospective_collect_data.add(fetch_sprint_times)

    fetch_sprint_relations = Task()
    fetch_sprint_relations.title = "Fetch Sprint relations"
    fetch_sprint_relations.priority = 2
    fetch_sprint_relations.time_estimation = 2
    fetch_sprint_relations.dod = {
        1: "Fetch parents_ids and children_ids relations",
        2: "Input sprint ID",
        3: "Output List of items with times and relations"
    }
    sprint_retrospective_collect_data.add(fetch_sprint_relations)

    # region work_plan
    work_plan_generation = UserStory()
    work_plan_generation.title = "Work plan from code"
    work_plan_generation.priority = 2
    work_plan_generation.dod = {
        1: "Python file work items input. Output - list of dicts",
        2: "Validation title length < 10",
        3: "Validation priority set",
        4: "Validation dod set",
        5: "Validation time_estimation set",
        6: "Validation description set",
        7: "Hapi_uid generated per item",
        8: "Child relations set by Hapi_uid",
    }
    feature_sms.add(work_plan_generation)
    # end_region

    convert_objects_to_list = Task()
    convert_objects_to_list.title = "Work plan from code"
    convert_objects_to_list.priority = 2
    convert_objects_to_list.dod = {
        1: "Python file work items input. Output - list of dicts"
                                  }

    work_plan_generation.add(convert_objects_to_list)

    input_validation = Task()
    input_validation.title = "Validation user input"
    input_validation.priority = 2
    input_validation.dod = {
        2: "Validation title length < 10",
        3: "Validation priority set",
        4: "Validation dod set",
        5: "Validation time_estimation set",
        6: "Validation description set",
    }

    work_plan_generation.add(input_validation)

    item_relations = Task()
    item_relations.title = "Validation user input"
    item_relations.priority = 2
    item_relations.dod = {
        7: "Hapi_uid generated per item",
        8: "Child relations set by Hapi_uid",
    }

    work_plan_generation.add(item_relations)

    human_api.generate_work_plan([feature_sms])


if __name__ == "__main__":
    test_sprint_planning()
