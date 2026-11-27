"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""

import json
import re
import time
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

import requests
from horey.h_logger import get_logger
from horey.github_api.github_api_configuration_policy import (
    GithubAPIConfigurationPolicy,
)
from horey.github_api.actions.workflow import Workflow
from horey.github_api.actions.job import Job
from horey.github_api.actions.workflow_run import WorkflowRun
from horey.git_api.git_api import GitAPI, GitAPIConfigurationPolicy

logger = get_logger()


class GithubAPI:
    """
    Main Class.
    """

    def __init__(self, configuration: GithubAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.server_address = "https://api.github.com"

    def create_request(self, request: str):
        """
        Construct request.

        #request = "https://github.com/api/v4/groups/{group_id}/projects"
        @param request:
        @return:
        """

        request = request.replace(self.server_address, "")

        if request.startswith("/"):
            request = request[1:]

        return f"{self.server_address}/{request}"

    def get(self, request_path, params=None):
        """
        Compose and send GET request.

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        headers = {"Authorization": f"Bearer {self.configuration.pat}"}
        response = requests.get(request, headers=headers, timeout=60, params=params)
        try:
            response.raise_for_status()
        except Exception:
            logger.error(f"{response.status_code}: {response.text}")
            raise

        try:
            return response.json()
        except Exception:
            return response.text


    def post(self, request_path, data):
        """
        Compose and send POST request

        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)
        return self.post_raw(request, data)

    def post_raw(self, request, data):
        """
        Send POST request.

        @param request:
        @param data:
        @return:
        """

        headers = {"Authorization": f"Bearer {self.configuration.pat}",
                   "Content-Type": "application/vnd.github+json",
                   "Accept": "application/vnd.github+json"}

        response = requests.post(request, data=json.dumps(data), headers=headers, timeout=60)

        if response.status_code in [200, 201]:
            return response.json()

        if response.status_code in [204]:
            return {"status_code": response.status_code}

        raise RuntimeError(
                f"Request to github api returned an error {response.status_code}, the response is:\n{response.text}"
            )

    def put(self, request_path, data):
        """
        Compose and send POST request

        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)
        headers = {"Authorization": f"Bearer {self.configuration.pat}",
                   "Content-Type": "application/vnd.github+json",
                   "Accept": "application/vnd.github+json"}

        response = requests.put(request, data=json.dumps(data), headers=headers, timeout=60)
        response.raise_for_status()


    def init_repositories(self):
        """
        Init all repositories in group.
        curl -L \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer <YOUR-TOKEN>" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/orgs/ORG/repos

        :return:
        """

        repos = []
        page = 1
        while True:
            response = self.get(f"orgs/{self.configuration.owner}/repos?per_page=100&page={page}")
            logger.info(f"Page: {page}, Items: {len(response)}")
            if not response:
                break
            repos.extend(response)
            page += 1
        logger.info(f"Total repos: {len(repos)}")
        return repos

    def create_repository(self, name, description=None):
        """
        Create repository.
        curl -L \
        -X POST \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer <YOUR-TOKEN>" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/orgs/ORG/repos \
        -d '{"name":"Hello-World",
        "description":"This is your first repository",
        "homepage":"https://github.com",
        "private":false,
        "has_issues":true,
        "has_projects":true,
        "has_wiki":true}'

        :param description:
        :param name:
        :return:
        """

        data = {
            "name": name,
            "private": True,
            "has_projects": True,
            "has_wiki": True,
            "has_issues": True,
            "description": description or name
        }
        response = self.post(f"/orgs/{self.configuration.owner}/repos", data)
        logger.info(response)
        return response

    def copy_repository_permissions(self, src_repo_name:str, dst_repo_name:str):
        """
        Copy permissions from one repo to another.

        :param src_repo_name:
        :param dst_repo_name:
        :return:
        """

        teams = self.get_repository_direct_teams(src_repo_name)
        for team in teams:
            for level in ["admin", "maintain", "push", "triage", "pull"]:
                if team["permissions"][level]:
                    data = {
                        "permission": level
                        }
                    self.put(f"/orgs/{self.configuration.owner}/teams/{team['slug']}/repos/{self.configuration.owner}/{dst_repo_name}", data)
                    break
        return True

    def get_repository_direct_teams(self, repo_name):
        """
        List teams with direct repository access (not organization-level access).

        :param repo_name: Repository name
        :return: List of teams with direct access only
        """

        all_teams = self.get(f"repos/{self.configuration.owner}/{repo_name}/teams")
        direct_teams = []

        for team in all_teams:
            # Check if team has explicit repository permissions
            try:

                self.get(
                f"orgs/{self.configuration.owner}/teams/{team['slug']}/repos/{self.configuration.owner}/{repo_name}")
                direct_teams.append(team)
            except Exception as inst_err:
                if "Not Found for url" not in repr(inst_err):
                    raise

        return direct_teams

    def get_repository_rule_sets(self, repo_name):
        """
        List teams with direct repository access (not organization-level access).

        :param repo_name: Repository name
        :return: List of teams with direct access only
        """

        return self.get(f"repos/{self.configuration.owner}/{repo_name}/rulesets")

    def get_branch_rules(self, repo_name, branch_name):
        """
        Get all rules active on a branch - from repo and org level rulesets.

        :param repo_name:
        :param branch_name:
        :return: list of rules [{"type": ..., "parameters": ..., "ruleset_id": ...}]
        """

        rules = []
        page = 1
        while True:
            response = self.get(f"repos/{self.configuration.owner}/{repo_name}/rules/branches/{branch_name}",
                                params={"per_page": 100, "page": page})
            if not response:
                break
            rules.extend(response)
            page += 1
        return rules

    def get_branch_required_status_checks(self, repo_name, branch_name):
        """
        Get required status check contexts enforced by rulesets on a branch.

        :param repo_name:
        :param branch_name:
        :return: list of status check context names
        """

        contexts = []
        for rule in self.get_branch_rules(repo_name, branch_name):
            if rule.get("type") != "required_status_checks":
                continue
            for check in rule.get("parameters", {}).get("required_status_checks", []):
                contexts.append(check["context"])
        return contexts

    def get_repository_rule_set(self, repo_name, ruleset_id):
        """
        Get a single repository ruleset with its full rules list.

        :param repo_name:
        :param ruleset_id:
        :return: ruleset dict
        """

        return self.get(f"repos/{self.configuration.owner}/{repo_name}/rulesets/{ruleset_id}")

    def replace_required_status_checks(self, repo_name, old_substring, new_substring):
        """
        Rename required status check contexts in every repo-level ruleset.
        Other checks and rules are kept as is.

        Example: old_substring="<old-org>", new_substring="<new-org>" turns
        "code/snyk (<old-org>)" into "code/snyk (<new-org>)".

        :param repo_name:
        :param old_substring:
        :param new_substring:
        :return: list of changed ruleset ids
        """

        changed = []
        for summary in self.get_repository_rule_sets(repo_name):
            if summary.get("source_type") != "Repository":
                continue
            ruleset = self.get_repository_rule_set(repo_name, summary["id"])
            modified = False
            for rule in ruleset.get("rules", []):
                if rule.get("type") != "required_status_checks":
                    continue
                for check in rule.get("parameters", {}).get("required_status_checks", []):
                    if old_substring in check["context"]:
                        check["context"] = check["context"].replace(old_substring, new_substring)
                        modified = True
            if not modified:
                continue

            # PUT replaces the ruleset as a whole, so send back the full rules list.
            data = {key: ruleset[key] for key in ("name", "target", "enforcement", "conditions", "rules", "bypass_actors")
                    if key in ruleset}
            logger.info(f"Updating ruleset {ruleset['id']} '{ruleset['name']}' in {repo_name}")
            self.put(f"repos/{self.configuration.owner}/{repo_name}/rulesets/{ruleset['id']}", data)
            changed.append(ruleset["id"])
        return changed

    def get_repositories_missing_required_status_check(self, name_regex, status_check, include_archived=False):
        """
        Find repos whose default branch rulesets do not require the status check.

        :param name_regex: e.g. "^horey-"
        :param status_check: substring of the required check context (case-insensitive),
            e.g. "Horey" matches "check/snyk (horey)"
        :param include_archived:
        :return: list of dicts {"name", "default_branch", "required_status_checks"}
        """

        pattern = re.compile(name_regex)
        ret = []
        for repo in self.init_repositories():
            if not pattern.search(repo["name"]):
                continue
            if repo.get("archived") and not include_archived:
                continue
            contexts = self.get_branch_required_status_checks(repo["name"], repo["default_branch"])
            if any(status_check.lower() in context.lower() for context in contexts):
                continue
            ret.append({"name": repo["name"],
                        "default_branch": repo["default_branch"],
                        "required_status_checks": contexts})
        return ret

    def init_self_hosted_runners(self):
        """
        Initialize self-hosted runners.

        :return:
        """

        runners = []
        page = 1
        while True:
            response = self.get(
                f"orgs/{self.configuration.owner}/actions/runners?per_page=100&page={page}"
            )
            logger.info(f"Page: {page}, Items: {len(response)}")
            if not response:
                break
            runners.extend(response)
            page += 1
        logger.info(f"Total runners: {len(runners)}")
        return runners

    def init_github_hosted_runners(self):
        """
        Initialize github-hosted runners.

        :return:
        """

        runners = []
        page = 1
        while True:
            response = self.get(
                f"orgs/{self.configuration.owner}/actions/hosted-runners?per_page=100&page={page}"
            )
            logger.info(f"Page: {page}, Items: {len(response)}")
            if not response:
                break
            runners.extend(response)
            page += 1
        logger.info(f"Total runners: {len(runners)}")
        return runners

    def init_repository_self_hosted_runners(self, repo_name):
        """
        Initialize self-hosted runners for a specific repository.

        :param repo_name: Name of the repository
        :return:
        """

        runners = []
        page = 1
        while True:
            response = self.get(
                f"repos/{self.configuration.owner}/{repo_name}/actions/runners?per_page=100&page={page}"
            )

            if response["total_count"] == 0:
                break

            if len(runners) == response["total_count"]:
                break

            page_runners = response["runners"]
            logger.info(f"Page: {page}, Items: {len(page_runners)}")
            runners.extend(page_runners)
            page += 1
        logger.info(f"Total runners: {len(runners)}")
        return runners

    def request_runner_registration_token(self, name):
        """
        https://api.github.com<OWNER>/<REPO>/actions/runners/registration-token

        :return:
        """
        data = {"name": name}
        response = self.post(
            f"orgs/{self.configuration.owner}/actions/runners/registration-token", data
        )
        return response

    def request_repository_runner_registration_token(self, repository_name: str):
        """
        Request a runner registration token for a repository.

        :param repository_name: Name of the repository
        :return:
        """

        response = self.post(
            f"repos/{self.configuration.owner}/{repository_name}/actions/runners/registration-token",{}
        )

        return response

    @staticmethod
    def init_hagent_docker_build_dir(build_dir: Path):
        """
        Initialize docker build directory.

        :param build_dir: Build directory path
        :return:
        """

        build_dir.mkdir(parents=True, exist_ok=True)
        for file_name in ["Dockerfile", "entrypoint.sh"]:
            shutil.copy(Path(__file__).parent / "build" /file_name, build_dir / file_name)
        return True


    def delete_repository_runner(self, repo_name, runner_name):
        """
        Delete a repository runner.

        :param repo_name:
        :param runner_name:
        :return:
        """
        runners = self.init_repository_self_hosted_runners(repo_name)
        for runner in runners:
            if runner["name"] == runner_name:
                self.delete_repository_runner_by_id(repo_name, runner["id"])
                return True
        return False

    def delete_repository_runner_by_id(self, repo_name, runner_id):
        """
        Delete a repository runner by id.

        :param repo_name:
        :param runner_id:
        :return:
        """

        self.delete(f"repos/{self.configuration.owner}/{repo_name}/actions/runners/{runner_id}")

    def delete(self, request_path):
        """
        Compose and send DELETE request

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)
        headers = {"Authorization": f"Bearer {self.configuration.pat}",
                   "Content-Type": "application/vnd.github+json",
                   "Accept": "application/vnd.github+json"}

        response = requests.delete(request, headers=headers, timeout=60)
        response.raise_for_status()

    # pylint: disable = too-many-locals, too-many-statements
    def get_workflow_dependency_tree(self, workflow_file_path: Path, git_dir_path:Path=None):
        """
        Get the flow tree.
        """

        ret_tree = ""
        if git_dir_path is None:
            git_dir_path = workflow_file_path
            while True:
                if git_dir_path.name == ".github":
                    git_dir_path = git_dir_path.parent.parent
                    break
                git_repo_path_parent = git_dir_path.parent
                if str(git_repo_path_parent) == str(git_dir_path):
                    raise ValueError("Reached root without finding git repo dir")
                git_dir_path = git_repo_path_parent

        if not git_dir_path.exists():
            raise RuntimeError(f"{git_dir_path=} does not exist")
        git_dir_path = git_dir_path.resolve()

        configuration = GitAPIConfigurationPolicy()

        configuration.git_directory_path = git_dir_path
        relative = workflow_file_path.relative_to(git_dir_path)
        repo_directory_name = str(relative).split("/", maxsplit=1)[0]
        repo_dir_path = configuration.git_directory_path/repo_directory_name
        configuration.directory_path = repo_dir_path

        caller_git_api = GitAPI(configuration=configuration)
        caller_git_api.init_configuration_attributes_from_bash()

        parent_node_name = caller_git_api.configuration.repository_name + "_" + workflow_file_path.name

        caller_workflow = Workflow()
        caller_workflow.init_from_file(workflow_file_path)
        for job in caller_workflow.jobs:
            if not job.uses:
                continue
            uses_parts = job.uses.split("/", 2)
            called_org_name = uses_parts[0]
            if caller_git_api.configuration.organisation_name != called_org_name:
                raise NotImplementedError(f"Same org/enterprice expected: {caller_git_api.configuration.organisation_name=}, {called_org_name=}")

            ref = None
            if "@" in uses_parts[-1]:
                yaml_path, ref = uses_parts[-1].split("@")
            else:
                yaml_path = uses_parts[-1]
            repo_name = uses_parts[1]
            config = GitAPIConfigurationPolicy()
            config.directory_path = git_dir_path / repo_name
            if not config.directory_path.exists():
                raise NotImplementedError("Validate git repository creation before checkout")

            git_api = GitAPI(config)
            git_api.init_configuration_attributes_from_bash()
            if ref:
                git_api.checkout_remote(ref)

            child_node_name, sub_tree = self.get_workflow_dependency_tree(git_dir_path / repo_name / yaml_path, git_dir_path)
            ref_name = ref or "master"
            src = f"{parent_node_name}[{workflow_file_path.name}\njob:{job.name}]"
            dst = f"|{git_api.configuration.repository_name}>{ref_name}| {child_node_name}"
            ret_tree += "\n" + f"{src} --> {dst}"
            ret_tree += sub_tree

        return parent_node_name, ret_tree

    def trigger_action(self, repo_name, action_name, branch_name, asynchronous:bool=False, parameters:dict=None):
        """
        Trigger Action

        curl -X POST \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/horey/my_repo/actions/workflows/test-action-name/dispatches \
        -d '{"ref":"horey"}'


        YYYY-MM-DDTHH:MM:SS+00:00	cats created:2017-01-01T01:00:00+07:00..2017-03-01T15:30:15+07:00
        ('created_at', '2026-10-09T15:07:34Z')
        """

        if ".yml" not in action_name and ".yaml" not in action_name:
            raise ValueError("Only action_name format supported is YAML filename including extention .yml or .yaml")

        created_after = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        url = f"https://api.github.com/repos/{repo_name}/actions/workflows/{action_name}/dispatches"
        data = parameters or {}
        data["ref"] = branch_name
        ret = self.post(url, data)
        if asynchronous:
            return ret

        wf_run = self.get_last_workflow_run_by_branch(created_after, repo_name, action_name, branch_name)

        return self.wait_for_workflow_run_completion(wf_run)

    def update_info_worflow_run(self, wf_run:WorkflowRun):
        """
        Standard
        """

        try:
            ret_raw = self.get(wf_run.url)
        except requests.exceptions.HTTPError as inst_err:
            if "Not Found" not in repr(inst_err):
                raise
            return False

        return wf_run.init_from_api(ret_raw)

    def get_last_workflow_run_by_branch(self, created_after:str, repo_name:str, action_name:str, branch_name:str) -> WorkflowRun:
        """
        Get flow started after created_after
        """

        url_runs = f"/repos/{repo_name}/actions/runs"
        params = {
            "created": f">{created_after}",
            "per_page": 100
        }

        retries = 100
        for _ in range(retries):
            try:
                ret_raw = self.get(url_runs, params=params)
                if not ret_raw["workflow_runs"]:
                    raise RuntimeError("Zero worflow runs")
                break
            except RuntimeError:
                logger.info("Workflow run is not yet created going to sleep waiting.")
                time.sleep(0.1)
        else:
            raise TimeoutError(f"Was not able to get created workflow runs in {retries=}")

        ret = []

        for dict_src in ret_raw["workflow_runs"]:
            wf_run = WorkflowRun()
            wf_run.init_from_api(dict_src)
            if action_name not in wf_run.path:
                continue
            if wf_run.head_branch != branch_name:
                continue
            ret.append(wf_run)

        if len(ret) != 1:
            raise ValueError(f"Expected single run. Got: {ret_raw['workflow_runs']}")

        logger.info(ret[0].html_url)

        return ret[0]

    def wait_for_workflow_run_completion(self, wf_run: WorkflowRun, timeout_seconds:int=60*60*2):
        """
        Wait for run
        """

        start_time = datetime.now()
        timeout_time = start_time + timedelta(seconds=timeout_seconds)

        while datetime.now() < timeout_time:
            if not self.update_info_worflow_run(wf_run):
                raise ValueError("Was not able to find or init the worflow run")

            if wf_run.status in ["in_progress", "queued"]:
                logger.info(f"Workflow {wf_run.id} run is not yet completed going to sleep waiting.")
                time.sleep(5)
                continue

            if wf_run.status in ["completed"]:
                logger.info(f"Took: {datetime.now()-start_time}")
                if wf_run.conclusion == "failure":
                    jobs_res = self.get(wf_run.jobs_url)
                    for job_dict in jobs_res["jobs"]:
                        job = Job("default")
                        job.init_from_dict(job_dict)
                        if job.conclusion != "failure":
                            continue
                        #for step in job.steps:
                        #    if step.conclusion != "failure":
                        #        continue
                        logger.info(f"{wf_run.html_url}/job/{job.id}")

                    return False
                return True

            raise ValueError(f"Unknown Worflow Run Status: {wf_run.status}")

        raise ValueError("Unknown Worflow Status")

    def get_workflow_runs(self, repo_name:str, action_name:str=None, created_after:str="", branch_name:str="") -> list[WorkflowRun]:
        """
        Get flow started after created_after
        """

        url_runs = f"/repos/{self.configuration.owner}/{repo_name}/actions/runs"
        params = {
            "per_page": 100
        }
        if created_after:
            params["created"]= f">{created_after}"

        retries = 100
        for _ in range(retries):
            try:
                ret_raw = self.get(url_runs, params=params)
                if not ret_raw["workflow_runs"]:
                    raise RuntimeError("Zero worflow runs")
                break
            except RuntimeError:
                logger.info("Workflow run is not yet created going to sleep waiting.")
                time.sleep(0.1)
        else:
            raise TimeoutError(f"Was not able to get created workflow runs in {retries=}")

        runs = []
        for dict_src in ret_raw["workflow_runs"]:
            wf_run = WorkflowRun()
            wf_run.init_from_api(dict_src)

            if action_name and action_name not in wf_run.path:
                continue
            if branch_name and wf_run.head_branch != branch_name:
                continue
            runs.append(wf_run)

        return runs

    def get_workflow_run_jobs(self, wf_run:WorkflowRun):
        """
        Get run jobs
        """

        res = self.get(wf_run.jobs_url)
        ret = []
        for dict_src in res["jobs"]:
            job = Job(dict_src["name"])
            if not job.init_from_dict(dict_src):
                raise ValueError("Was not able to init")
            ret.append(job)
        return ret

    def extract_job_step_input_parameters(self, job:Job, step_name):
        """
        Extract inputs
        """

        for step in job.steps:
            if step.name == step_name:
                break
        else:
            raise ValueError(f"Was not able to find step with name {step_name}")

        req_url = f"{job.url}/steps/{step.number}/logs"
        str_log = self.get(req_url)
        log_lines = str_log.split("\n")

        block_lines = self.get_block(log_lines, " ##[group]", " ##[endgroup]")
        with_lines = self.get_block(block_lines, " with:", " env:")
        date_free_lines = [x.split(" ", 1)[1].strip(" ") for x in with_lines[1:-1]]
        dict_ret = {}
        for line in date_free_lines:
             key, value = line.split(":", 1)
             key = key.strip(" ")
             value = value.strip(" ")
             dict_ret[key] = value
        return dict_ret

    @staticmethod
    def get_block(log_lines, start_block, end_block):
        """
        Get block by start end
        """
        block_aggregator = []
        for log_line in log_lines:
            if start_block not in log_line and not block_aggregator:
                continue
            block_aggregator.append(log_line)
            if end_block in log_line:
                break
        else:
            raise ValueError("Was not able to find input block")

        return block_aggregator

    def get_repository_workflows(self, repo_name):
        """
        List all workflows under repo

        :param repo_name: Repository name
        :return: List of workflows
        """

        all_worflows = self.get(f"repos/{self.configuration.owner}/{repo_name}/actions/workflows")
        ret = []
        logger.info(f"Fetched {all_worflows['total_count']} workflows") 

        for dict_src in all_worflows.get("workflows", []):
            wf = Workflow()
            wf.init_from_api(dict_src)
            ret.append(wf)

        return ret
