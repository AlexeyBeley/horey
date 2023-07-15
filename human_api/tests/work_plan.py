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

    feature_wms = Feature()
    feature_wms.title = "Work Management system"
    feature_wms.priority = 1
    feature_wms.sprint_name = "Backlog"
    feature_wms.description = "Create the system to manage work flow. Plan work flow and do a retrospective."
    feature_wms.dod = {1: "Sprint retrospective logs current time spent",
                        2: "Sprint retrospective resets tasks' times.",
                        3: "Creates work plan - user stories tasks and bugs"}

    sprint_retrospective = UserStory()
    sprint_retrospective.title = "Sprint retrospective"
    sprint_retrospective.description = "Create retrospective and save it to reliable place- Task Management System."
    sprint_retrospective.priority = 1
    sprint_retrospective.sprint_name = "Sprint_1"
    sprint_retrospective.dod = {
        1: "Work status is saved in json format in a local file",
        2: "Current status is saved in json format as a comment in TMS's comment",
        3: "Work status is saved in python format without CLOSED. Will be used as a basic for work_plan.py for the next sprint"
    }
    feature_wms.add(sprint_retrospective)

    sprint_retrospective_collect_data = UserStory()
    sprint_retrospective_collect_data.title = "Generate Sprint status"
    sprint_retrospective_collect_data.description = "Get work items from the TSM as dicts with all needed data to build retro."
    sprint_retrospective_collect_data.priority = 1
    sprint_retrospective_collect_data.sprint_name = "Sprint_1"
    sprint_retrospective_collect_data.dod = {
        1: "Fetch NEW, ACTIVE, BLOCKED and CLOSED tasks, bugs and user_stories assigned to this sprint",
        2: "Fetch Assumed time and Reported working time",
        3: "Fetch parents_ids and children_ids relations",
        4: "Return List with all collected data"
    }
    sprint_retrospective.add(sprint_retrospective_collect_data)

    fetch_sprint_items = Task()
    fetch_sprint_items.title = "Fetch Sprint items"
    fetch_sprint_items.description = "Fetch items from TSM and convert to dicts."
    fetch_sprint_items.priority = 1
    fetch_sprint_items.sprint_name = "Sprint_1"
    fetch_sprint_items.estimated_time = 4
    fetch_sprint_items.dod = {
        1: "Fetch NEW, ACTIVE, BLOCKED and CLOSED tasks, bugs and user_stories assigned to this sprint",
        2: "Input sprint ID",
        3: "Output List of items with"
    }
    sprint_retrospective_collect_data.add(fetch_sprint_items)

    fetch_sprint_owners = Task()
    fetch_sprint_owners.title = "Fetch Sprint Item owners"
    fetch_sprint_owners.priority = 2
    fetch_sprint_owners.sprint_name = "Sprint_1"

    fetch_sprint_owners.description = "Fetch items' owners (assigned_to) data. " \
                                      "If owner was not set- Item's creator is used."
    fetch_sprint_owners.estimated_time = 2
    fetch_sprint_owners.dod = {
        1: "Fetch item owners",
        2: "Input sprint ID",
        3: "Output List of items with owners"
    }
    sprint_retrospective_collect_data.add(fetch_sprint_owners)

    fetch_sprint_times = Task()
    fetch_sprint_times.title = "Fetch Sprint times"
    fetch_sprint_times.sprint_name = "Sprint_1"
    fetch_sprint_times.priority = 2
    fetch_sprint_times.description = "Fetch interesting times- estimated and reported."
    fetch_sprint_times.estimated_time = 2
    fetch_sprint_times.dod = {
        1: "Fetch Assumed time and Reported working time",
        2: "Input sprint ID",
        3: "Output List of items with times"
    }
    sprint_retrospective_collect_data.add(fetch_sprint_times)

    fetch_sprint_relations = Task()
    fetch_sprint_relations.title = "Fetch Sprint relations"
    fetch_sprint_relations.description = "Actually the relations are fetched as part of a global fetch, but we need to represent them."
    fetch_sprint_relations.sprint_name = "Sprint_1"
    fetch_sprint_relations.priority = 2
    fetch_sprint_relations.estimated_time = 2
    fetch_sprint_relations.dod = {
        1: "Fetch parents_ids and children_ids relations",
        2: "Input sprint ID",
        3: "Output List of items with times and relations"
    }
    sprint_retrospective_collect_data.add(fetch_sprint_relations)

    # region work_plan
    work_plan_generation = UserStory()
    work_plan_generation.title = "Work plan from code"
    work_plan_generation.description = "Split recursively the input work items to a tree of dictionaries. " \
                                       "Validate the input and generate human readable output."
    work_plan_generation.priority = 2
    work_plan_generation.sprint_name = "Sprint_0"
    work_plan_generation.dod = {
        1: "Python file work items input. Output - list of dicts",
        2: "Validation title length < 10",
        3: "Validation priority set",
        4: "Validation dod set",
        5: "Validation estimated_time set",
        6: "Validation description set",
        7: "Hapi_uid generated per item",
        8: "Child relations set by Hapi_uid",
        9: "User friendly sprint planning summary for review.",
        10: "Validation copy/past - title, description, dod",
        11: "Work plan is written to file in the format of work status.",
        12: "All spent time is reset to 0",
        13: "Validation child sprints are the same as parent's"
    }
    feature_wms.add(work_plan_generation)
    # end_region

    convert_objects_to_list = Task()
    convert_objects_to_list.title = "Serialize work plan"
    convert_objects_to_list.estimated_time = 1
    convert_objects_to_list.description = "Generate dictionaries with relevant data per item- return list of them."
    convert_objects_to_list.priority = 2
    convert_objects_to_list.sprint_name = "Sprint_0"
    convert_objects_to_list.dod = {
        1: "Python file work items input. Output - list of dicts"
                                  }

    work_plan_generation.add(convert_objects_to_list)

    input_validation = Task()
    input_validation.title = "User input validation"
    input_validation.description = "Validate the values against the defined policy."
    input_validation.sprint_name = "Sprint_0"
    input_validation.priority = 2
    input_validation.estimated_time = 3
    input_validation.dod = {
        2: "Validation title length < 10",
        3: "Validation priority set",
        4: "Validation dod set",
        5: "Validation estimated_time set",
        6: "Validation description set",
        7: "Validation child sprints are the same as parent's",
        8: "Validation sprint_name is set",
    }

    work_plan_generation.add(input_validation)

    item_relations = Task()
    item_relations.title = "Item children and parents"
    item_relations.description = "Find children and parents create tree of a parent down to children"
    item_relations.sprint_name = "Sprint_0"
    item_relations.priority = 2
    item_relations.estimated_time = 2
    item_relations.dod = {
        7: "Hapi_uid generated per item",
        8: "Child relations set by Hapi_uid",
    }

    work_plan_generation.add(item_relations)

    # region Task
    report_human_summary = Task()
    report_human_summary.title = "Summary for manual review"
    report_human_summary.description = "Generate a short review for other team member/manager to review. If anybody can understand then the plan is ok."
    report_human_summary.priority = 2
    report_human_summary.sprint_name = "Sprint_0"
    report_human_summary.estimated_time = 2
    report_human_summary.dod = {
        7: "Human readable form - h_text generated per user story.",
    }

    work_plan_generation.add(report_human_summary)
    # endregion

    # region Task
    report_human_summary = Task()
    report_human_summary.title = "Duplication Validation"
    report_human_summary.description = "Validate string params are not copy/pasted."
    report_human_summary.sprint_name = "Sprint_0"
    report_human_summary.priority = 2
    report_human_summary.estimated_time = 2
    report_human_summary.dod = {
        7: "Raises exception if [description, title, dod, hapi_uid] value appears more then once"
    }

    work_plan_generation.add(report_human_summary)
    # endregion

    # Do the plan
    human_api.generate_work_plan([feature_wms])


if __name__ == "__main__":
    test_sprint_planning()
