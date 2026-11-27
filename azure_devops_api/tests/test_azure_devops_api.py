"""
Testing chronograf api
"""
import os
import pytest

from horey.azure_devops_api.azure_devops_api import AzureDevopsAPI
from horey.azure_devops_api.azure_devops_api_configuration_policy import (
    AzureDevopsAPIConfigurationPolicy,
)
from horey.common_utils.common_utils import CommonUtils

configuration = AzureDevopsAPIConfigurationPolicy()
ignore_dir_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore"
    ))
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        ignore_dir_full_path,
        "azure_devops_api_configuration_values.py",
    )
)

mock_file_file_full_path = os.path.abspath(
    os.path.join(
        ignore_dir_full_path,
        "azure_devops_api_mock_values.py",
    )
)
mock_values = CommonUtils.load_object_from_module(mock_file_file_full_path, "main")

configuration.init_from_file()

azure_devops_api = AzureDevopsAPI(configuration=configuration)


# pylint: disable= missing-function-docstring


@pytest.mark.done
def test_init_backlogs():
    azure_devops_api.init_backlogs()
    assert len(azure_devops_api.backlogs) > 0


@pytest.mark.done
def test_init_work_items():
    azure_devops_api.init_work_items()
    assert len(azure_devops_api.work_items) > 0


@pytest.mark.done
def test_init_team_members():
    azure_devops_api.init_team_members()
    assert len(azure_devops_api.team_members) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_processes():
    azure_devops_api.init_processes()
    assert len(azure_devops_api.processes) > 0


@pytest.mark.done
def test_init_iterations():
    azure_devops_api.init_iterations(from_cache=True)
    assert len(azure_devops_api.iterations) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_and_cache_iterations():
    azure_devops_api.init_iterations()


@pytest.mark.done
def test_init_and_cache_work_items():
    azure_devops_api.init_work_items()


@pytest.mark.done
def test_current_iteration():
    assert azure_devops_api.get_iteration() is not None


@pytest.mark.skip(reason="Can not test")
def test_generate_clean_report():
    azure_devops_api.init_work_items(from_cache=True)
    azure_devops_api.init_iterations(from_cache=True)
    h_tb = azure_devops_api.generate_clean_report()
    print(h_tb)
    assert h_tb is not None


@pytest.mark.skip(reason="Can not test")
def test_init_and_cache_boards():
    lst_ret = azure_devops_api.init_boards()
    assert len(lst_ret) > 0


@pytest.mark.skip(reason="Can not test")
def test_recursive_init_work_items():
    azure_devops_api.init_work_items(from_cache=True)
    azure_devops_api.recursive_init_work_items(azure_devops_api.work_items)


@pytest.mark.skip(reason="Can not test")
def test_provision_work_item_by_params():
    wit_type = "user_story"
    wit_title = "test"
    iteration_partial_path = mock_values["iteration_partial_path"]
    original_estimate_time = "4.0"
    azure_devops_api.provision_work_item_by_params(wit_type, wit_title, "Some description",
                                                   iteration_partial_path=iteration_partial_path,
                                                   original_estimate_time=original_estimate_time)


@pytest.mark.skip(reason="Can not test")
def test_provision_work_item_by_params_with_parent():
    wit_type = "user_story"
    wit_title = "test"
    iteration_partial_path = mock_values["iteration_partial_path"]
    original_estimate_time = "4.0"
    azure_devops_api.provision_work_item_by_params(wit_type, wit_title, "test_comment",
                                                   iteration_partial_path=iteration_partial_path,
                                                   original_estimate_time=original_estimate_time,
                                                   parent_id=0000,
                                                   assigned_to="horey")


@pytest.mark.skip(reason="Can not test")
def test_add_wit_comment():
    azure_devops_api.add_wit_comment("", "test comment")


@pytest.mark.unit
def test_get_wit_comment():
    azure_devops_api.get_wit_comments("")


@pytest.mark.skip
def test_generate_solution_retrospective():
    azure_devops_api.init_work_items(from_cache=True)
    search_strings = mock_values["search_strings"]
    htb_ret = azure_devops_api.generate_solution_retrospective(search_strings)
    htb_ret.write_to_file("tmp.htb")
    assert htb_ret is not None
    assert len(azure_devops_api.work_items) > 0


@pytest.mark.done
def test_generate_retrospective_times():
    azure_devops_api.init_work_items(from_cache=True)
    search_strings = mock_values["search_strings"]
    htb_ret = azure_devops_api.generate_retrospective_times(search_strings)
    htb_ret.write_to_file("tmp_times.htb")
    assert htb_ret is not None
    assert len(azure_devops_api.work_items) > 0


@pytest.mark.unit
def test_add_hours_to_work_item():
    azure_devops_api.add_hours_to_work_item("", 0.0)
