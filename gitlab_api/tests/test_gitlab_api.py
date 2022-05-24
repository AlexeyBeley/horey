import pdb

import pytest
import os

from horey.gitlab_api.gitlab_api import GitlabAPI
from horey.gitlab_api.gitlab_api_configuration_policy import GitlabAPIConfigurationPolicy

configuration = GitlabAPIConfigurationPolicy()
configuration.configuration_file_full_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "ignore",
                 "gitlab_api_configuration_values.py"))
configuration.init_from_file()

gitlab_api = GitlabAPI(configuration=configuration)


@pytest.mark.skip(reason="Can not test")
def test_init_gitlab_api():
    gitlab_api = GitlabAPI(configuration=configuration)
    assert isinstance(gitlab_api, GitlabAPI)


@pytest.mark.skip(reason="Can not test")
def test_init_projects():
    gitlab_api.init_projects()
    assert isinstance(gitlab_api.projects, list)


@pytest.mark.skip(reason="Can not test")
def test_add_user_to_projects():
    gitlab_api.init_projects()
    user_id = ""
    pdb.set_trace()
    gitlab_api.add_user_to_projects(gitlab_api.projects, user_id=user_id)
    assert isinstance(gitlab_api.projects, list)

if __name__ == "__main__":
    #test_init_gitlab_api()
    #test_init_projects()
    test_add_user_to_projects()
    #test_provision_dashboard()
