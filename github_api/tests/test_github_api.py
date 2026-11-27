"""
Testing github api functionality.

"""
import json

import pytest

from horey.aws_api.base_entities.region import Region
from horey.github_api.github_api import GithubAPI, GithubAPIConfigurationPolicy

"""
Common test utilities for infrastructure_api tests.
"""
from typing import TypeVar
from pathlib import Path
import shutil

from horey.common_utils.common_utils import CommonUtils
from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger
from horey.aws_api.aws_api import AWSAPI

test_mock_values_file_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_github_api_mocks.py"
test_mock_values = CommonUtils.load_module(test_mock_values_file_path)



logger = get_logger()


T = TypeVar('T', bound=ConfigurationPolicy)
data_directory_path = Path("/tmp/data")


class TstConfigs(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._src_repo_name = None
        self._dst_repo_name = None
        self._dst_repo_names = None
        self._pat = None
        self._owner = None
        self._action_name = None
        self._all_repos_url = None
        self._input_extract_job_name = None
        self._input_extract_job_step_name = None

    @property
    def input_extract_job_step_name(self):
        return self._input_extract_job_step_name

    @input_extract_job_step_name.setter
    def input_extract_job_step_name(self, value):
        self._input_extract_job_step_name = value

    @property
    def input_extract_job_name(self):
        return self._input_extract_job_name

    @input_extract_job_name.setter
    def input_extract_job_name(self, value):
        self._input_extract_job_name = value

    @property
    def all_repos_url(self):
        return self._all_repos_url

    @all_repos_url.setter
    def all_repos_url(self, value):
        self._all_repos_url = value

    @property
    def action_name(self):
        return self._action_name

    @action_name.setter
    def action_name(self, value):
        self._action_name = value

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    @property
    def pat(self):
        return self._pat

    @pat.setter
    def pat(self, value):
        self._pat = value

    @property
    def dst_repo_name(self):
        return self._dst_repo_name

    @dst_repo_name.setter
    def dst_repo_name(self, value):
        self._dst_repo_name = value

    @property
    def dst_repo_names(self):
        return self._dst_repo_names

    @dst_repo_names.setter
    def dst_repo_names(self, value):
        self._dst_repo_names = value

    @property
    def src_repo_name(self):
        return self._src_repo_name

    @src_repo_name.setter
    def src_repo_name(self, value):
        self._src_repo_name = value


def init_from_secrets_api(configuration_class: type[T], secret_name: str) -> T:
    """Download secret to temporary file and return file path."""
    aws_api = AWSAPI()
    data_directory_path.mkdir(exist_ok=True, parents=True)
    file_path = aws_api.get_secret_file(secret_name, data_directory_path, region = Region.get_region(test_mock_values.region))

    configuration = configuration_class()
    configuration.configuration_file_full_path = file_path
    configuration.init_from_file()
    if data_directory_path.exists():
        shutil.rmtree(data_directory_path)

    return configuration

@pytest.fixture(name="tests_config")
def fixture_tests_config():
    configuration = init_from_secrets_api(TstConfigs, test_mock_values.secret_name)
    yield configuration


@pytest.fixture(name="github_api")
def fixture_github_api(tests_config):
    configuration = GithubAPIConfigurationPolicy()
    configuration.pat = tests_config.pat
    configuration.owner = tests_config.owner

    _github_api = GithubAPI(configuration=configuration)
    yield _github_api


@pytest.mark.unit
def test_init_github_api(github_api):
    assert isinstance(github_api, GithubAPI)


@pytest.mark.unit
def test_init_repositories(github_api):
    assert github_api.init_repositories()

@pytest.mark.unit
def test_create_repository(github_api):
    assert github_api.create_repository("test_repo_name")


@pytest.mark.unit
def test_copy_repository_permissions(github_api, tests_config):
    assert github_api.copy_repository_permissions(tests_config.src_repo_name, tests_config.dst_repo_name)

@pytest.mark.unit
def test_copy_repositories_permissions(github_api, tests_config):
    for dst_repo_name in json.loads(tests_config.dst_repo_names):
        assert github_api.copy_repository_permissions(tests_config.src_repo_name, dst_repo_name)


@pytest.mark.unit
def test_init_self_hosted_runners(github_api, tests_config):
    assert github_api.init_self_hosted_runners()


@pytest.mark.unit
def test_init_github_hosted_runners(github_api, tests_config):
    assert github_api.init_github_hosted_runners()



@pytest.mark.unit
def test_init_repository_self_hosted_runners(github_api, tests_config):
    assert github_api.init_repository_self_hosted_runners(tests_config.src_repo_name)


@pytest.mark.unit
def test_request_runner_registration_token(github_api, tests_config):
    assert github_api.request_runner_registration_token("test")

@pytest.mark.unit
def test_request_repository_runner_registration_token(github_api, tests_config):
    assert github_api.request_repository_runner_registration_token(tests_config.src_repo_name)


@pytest.mark.unit
def test_copy_repository_rule_sets(github_api, tests_config):
    assert github_api.copy_repository_rule_sets(tests_config.src_repo_name, tests_config.dst_repo_name)

@pytest.mark.unit
def test_get_workflow_dependency_tree(github_api):
    assert github_api.get_workflow_dependency_tree(Path(__file__).parent / "workflows" / "workflow1.yaml")

@pytest.mark.unit
def test_get_workflow_runs(github_api, tests_config):
    assert github_api.get_workflow_runs(tests_config.dst_repo_name, action_name=tests_config.action_name)

@pytest.mark.unit
def test_get_workflow_run_jobs(github_api, tests_config):
    ret = github_api.get_workflow_runs(tests_config.dst_repo_name, action_name=tests_config.action_name)
    for wf_run in ret:
        assert github_api.get_workflow_run_jobs(wf_run)

@pytest.mark.unit
def test_extract_run_input_parameters(github_api, tests_config):
    ret = github_api.get_workflow_runs(tests_config.dst_repo_name, action_name=tests_config.action_name)
    for wf_run in ret:
        jobs = github_api.get_workflow_run_jobs(wf_run)
        for job in jobs:
            if job.name != tests_config.input_extract_job_name:
                continue
            assert github_api.extract_job_step_input_parameters(job, tests_config.input_extract_job_step_name)


@pytest.mark.unit
def test_get_repository_workflows(github_api, tests_config):
    assert github_api.get_repository_workflows(tests_config.dst_repo_name)


@pytest.mark.unit
def test_get_repositories_missing_required_status_check(github_api):
    repos = github_api.get_repositories_missing_required_status_check("^repo-horey-", "OrgHorey")
    for repo in repos:
        logger.info(f"MISSING: {repo['name']} ({repo['default_branch']}) required checks: {repo['required_status_checks']}")
    logger.info(f"Total repos missing the check: {len(repos)}")
    assert isinstance(repos, list)


def get_repository_required_status_checks(github_api, repo_name):
    """
    Map repo-level ruleset id to its required status check contexts.
    """

    ret = {}
    for summary in github_api.get_repository_rule_sets(repo_name):
        if summary.get("source_type") != "Repository":
            continue
        ruleset = github_api.get_repository_rule_set(repo_name, summary["id"])
        ret[ruleset["id"]] = [check["context"]
                              for rule in ruleset.get("rules", []) if rule.get("type") == "required_status_checks"
                              for check in rule.get("parameters", {}).get("required_status_checks", [])]
    return ret


@pytest.mark.unit
def test_replace_required_status_checks_no_match(github_api, tests_config):
    before = get_repository_required_status_checks(github_api, tests_config.dst_repo_name)
    changed = github_api.replace_required_status_checks(tests_config.dst_repo_name,
                                                        "<substring-that-does-not-exist>", "<new-substring>")
    assert changed == []
    assert get_repository_required_status_checks(github_api, tests_config.dst_repo_name) == before


@pytest.mark.skip(reason="Modifies real repo rulesets and restores them - run manually")
def test_replace_required_status_checks_round_trip(github_api, tests_config):
    repo_name = tests_config.dst_repo_name
    before = get_repository_required_status_checks(github_api, repo_name)
    contexts = [context for ruleset_contexts in before.values() for context in ruleset_contexts]
    if not contexts:
        pytest.skip(f"No repo-level required status checks in {repo_name}")

    old_substring = contexts[0]
    new_substring = f"{old_substring}-horey-test"
    expected_ids = [ruleset_id for ruleset_id, ruleset_contexts in before.items()
                    if any(old_substring in context for context in ruleset_contexts)]

    changed = github_api.replace_required_status_checks(repo_name, old_substring, new_substring)
    try:
        assert sorted(changed) == sorted(expected_ids)
        after = get_repository_required_status_checks(github_api, repo_name)
        for ruleset_id, ruleset_contexts in before.items():
            assert after[ruleset_id] == [context.replace(old_substring, new_substring) for context in ruleset_contexts]
    finally:
        restored = github_api.replace_required_status_checks(repo_name, new_substring, old_substring)
        assert sorted(restored) == sorted(changed)

    assert get_repository_required_status_checks(github_api, repo_name) == before
