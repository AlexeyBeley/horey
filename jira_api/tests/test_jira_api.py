"""
Testing jira API
"""
import os
import pytest

from horey.jira_api.jira_api import JiraAPI
from horey.jira_api.jira_api_configuration_policy import (
    JiraAPIConfigurationPolicy,
)


ignore_dir_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore"
)
cache_dir = os.path.join(ignore_dir_path, "jira_api_cache")
os.makedirs(cache_dir, exist_ok=True)
dashboards_cache_file = os.path.join(cache_dir, "dashboards.json")
folders_cache_file = os.path.join(cache_dir, "folders.json")
rules_cache_file = os.path.join(cache_dir, "rules.json")
dashboards_datasource_file = os.path.join(cache_dir, "datasources.json")

configuration = JiraAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(ignore_dir_path, "jira_api_configuration_values.py")
)
configuration.init_from_file()

jira_api = JiraAPI(configuration=configuration)

# pylint: disable= missing-function-docstring


@pytest.mark.skip(reason="Can not test")
def test_init_jira_api():
    """
    Test Jira API initiation
    @return:
    """
    _jira_api = JiraAPI(configuration=configuration)
    assert isinstance(_jira_api, JiraAPI)


if __name__ == "__main__":
    test_init_jira_api()
