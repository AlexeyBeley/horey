"""
Testing chronograf api
"""
import os
import pytest

from horey.azure_devops_api.azure_devops_api import AzureDevopsAPI
from horey.azure_devops_api.azure_devops_api_configuration_policy import (
    AzureDevopsAPIConfigurationPolicy,
)

configuration = AzureDevopsAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "ignore",
        "azure_devops_api_configuration_values.py",
    )
)
configuration.init_from_file()

azure_devops_api = AzureDevopsAPI(configuration=configuration)

# pylint: disable= missing-function-docstring


@pytest.mark.skip(reason="Can not test")
def test_init_backlogs():
    azure_devops_api.init_backlogs()
    assert len(azure_devops_api.backlogs) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_work_items():
    azure_devops_api.init_work_items()
    assert len(azure_devops_api.work_items) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_team_members():
    azure_devops_api.init_team_members()
    assert len(azure_devops_api.team_members) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_processes():
    azure_devops_api.init_processes()
    assert len(azure_devops_api.processes) > 0


@pytest.mark.skip(reason="Can not test")
def test_init_iterations():
    azure_devops_api.init_iterations(from_cache=True)
    assert len(azure_devops_api.iterations) > 0


def test_init_and_cache_iterations():
    azure_devops_api.init_iterations()


def test_init_and_cache_work_items():
    azure_devops_api.init_work_items()


def test_current_iteration():
    assert azure_devops_api.get_iteration() is not None


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


def test_recursive_init_work_items():
    azure_devops_api.init_work_items(from_cache=True)
    lst_ret = azure_devops_api.recursive_init_work_items(azure_devops_api.work_items)
    breakpoint()


if __name__ == "__main__":
    #test_init_backlogs()
    #test_init_processes()
    #test_init_team_members()

    #test_init_and_cache_iterations()
    #test_init_iterations()

    #test_init_and_cache_work_items()
    #test_init_work_items()

    #test_current_iteration()
    #test_init_and_cache_boards()
    #test_recursive_init_work_items()

    test_generate_clean_report()


