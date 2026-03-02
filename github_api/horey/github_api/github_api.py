"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json

import requests
from horey.h_logger import get_logger
from horey.github_api.github_api_configuration_policy import (
    GithubAPIConfigurationPolicy,
)

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

        if request.startswith("/"):
            request = request[1:]

        return f"{self.server_address}/{request}"

    def get(self, request_path):
        """
        Compose and send GET request.

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)

        headers = {"Authorization": f"Bearer {self.configuration.pat}"}
        response = requests.get(request, headers=headers)
        response.raise_for_status()
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

        response = requests.post(request, data=json.dumps(data), headers=headers)

        if response.status_code not in [200, 201]:
            raise RuntimeError(
                f"Request to github api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response.json()

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

        response = requests.put(request, data=json.dumps(data), headers=headers)
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
                pass

        return direct_teams

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
        :param token_name: Name of the token
        :return:
        """

        response = self.post(
            f"repos/{self.configuration.owner}/{repository_name}/actions/runners/registration-token",{}
        )

        return response
