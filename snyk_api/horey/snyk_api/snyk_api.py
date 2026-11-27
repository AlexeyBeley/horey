"""
Snyk API
"""
import json
import time
from urllib.parse import urlparse

import requests
from horey.h_logger import get_logger
from horey.snyk_api.snyk_api_configuration_policy import (
    SnykAPIConfigurationPolicy,
)

logger = get_logger()


class SnykAPI:
    """
    Main Class.
    """

    def __init__(self, configuration: SnykAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.server_address = "https://api.snyk.io"

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

        headers = {"Authorization": self.configuration.api_key}
        response = requests.get(request, headers=headers, timeout=60)
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return response.text


    def get_headers(self):
        """
        Snyk auth headers.

        @return:
        """

        return {"Authorization": self.configuration.api_key,
                "Content-Type": "application/json"}

    def post(self, request_path, data):
        """
        Compose and send POST request

        @param request_path:
        @param data:
        @return: requests.Response
        """

        request = self.create_request(request_path)
        return self.post_raw(request, data)

    def post_raw(self, request, data):
        """
        Send POST request.

        @param request:
        @param data:
        @return: requests.Response
        """

        response = requests.post(request, data=json.dumps(data), headers=self.get_headers(), timeout=60)

        if response.status_code not in [200, 201, 202]:
            raise RuntimeError(
                f"Request to snyk api returned an error {response.status_code}, the response is:\n{response.text}"
            )
        return response

    def put(self, request_path, data):
        """
        Compose and send PUT request

        @param request_path:
        @param data:
        @return:
        """

        request = self.create_request(request_path)
        response = requests.put(request, data=json.dumps(data), headers=self.get_headers(), timeout=60)
        response.raise_for_status()
        return response

    def delete(self, request_path):
        """
        Compose and send DELETE request

        @param request_path:
        @return:
        """

        request = self.create_request(request_path)
        response = requests.delete(request, headers=self.get_headers(), timeout=60)
        response.raise_for_status()
        return response

    REST_VERSION = "2024-10-15"

    def get_rest_paginated(self, request_path, limit=100):
        """
        GET all pages of a Snyk REST API collection, following links.next.

        @param request_path: e.g. /rest/orgs/{org_id}/projects
        @param limit:
        @return: list of data items
        """

        separator = "&" if "?" in request_path else "?"
        if "version=" not in request_path:
            request_path = f"{request_path}{separator}version={self.REST_VERSION}&limit={limit}"

        ret = []
        while request_path:
            response = self.get(request_path)
            ret += response.get("data", [])
            next_path = response.get("links", {}).get("next")
            if next_path and not next_path.startswith("/rest"):
                next_path = "/rest" + next_path
            request_path = next_path
        return ret

    def get_orgs(self):
        """
        Get all orgs accessible by the token.

        :return:
        """

        return self.get_rest_paginated("/rest/orgs")

    def get_org_by_name(self, name):
        """
        Find org by name or slug.

        :param name:
        :return:
        """

        for org in self.get_orgs():
            attributes = org.get("attributes", {})
            if name.lower() in [str(attributes.get("name")).lower(), str(attributes.get("slug")).lower()]:
                return org
        raise ValueError(f"Org '{name}' was not found")

    def get_projects(self, org_id=None):
        """
        Get all projects in org

        :param org_id: defaults to configuration.org_id
        :return:
        """

        org_id = org_id or self.configuration.org_id
        return self.get_rest_paginated(f"/rest/orgs/{org_id}/projects")

    def get_projects_by_org_name(self, org_name):
        """
        Get all projects in org by its name or slug.

        :param org_name:
        :return:
        """

        org = self.get_org_by_name(org_name)
        return self.get_projects(org_id=org["id"])

    def get_targets(self):
        """
        Get all targets in org

        :return:
        """

        projects = self.get(f"/rest/orgs/{self.configuration.org_id}/targets?version=2026-03-25")

        return projects

    def get_integrations(self, org_id=None):
        """
        Get all integrations in org: {integration_type: integration_id}

        :param org_id: defaults to configuration.org_id
        :return:
        """

        org_id = org_id or self.configuration.org_id
        return self.get(f"/v1/org/{org_id}/integrations")

    def get_integration_id(self, integration_type="github-cloud-app", org_id=None):
        """
        Get integration id by its type.

        :param integration_type: github-cloud-app, github, azure-repos, cli...
        :param org_id:
        :return:
        """

        integrations = self.get_integrations(org_id=org_id)
        try:
            return integrations[integration_type]
        except KeyError as inst:
            raise ValueError(f"Integration '{integration_type}' not found in org. Available: {list(integrations)}") from inst

    def import_github_repo(self, owner, name, branch, org_id=None, integration_type="github-cloud-app",
                           files=None, exclusion_globs=None):
        """
        Start importing a GitHub repo into a Snyk org.

        :param owner: GitHub org/user, e.g. controlupltd
        :param name: repo name
        :param branch: branch to import, e.g. main. Required: github-cloud-app rejects imports without it.
        :param org_id: defaults to configuration.org_id
        :param integration_type:
        :param files: optional list of manifest paths to import, e.g. ["requirements.txt"]
        :param exclusion_globs: optional comma separated globs, e.g. "tests, fixtures"
        :return: import job url
        """

        if not branch:
            raise ValueError(f"Branch must be set explicitly for {owner}/{name}")

        org_id = org_id or self.configuration.org_id
        integration_id = self.get_integration_id(integration_type=integration_type, org_id=org_id)

        target = {"owner": owner, "name": name, "branch": branch}

        data = {"target": target}
        if files:
            data["files"] = [{"path": path} for path in files]
        if exclusion_globs:
            data["exclusionGlobs"] = exclusion_globs

        logger.info(f"Importing GitHub repo {owner}/{name} into Snyk org {org_id}")
        response = self.post(f"/v1/org/{org_id}/integrations/{integration_id}/import", data)
        job_url = response.headers.get("Location")
        if not job_url:
            raise RuntimeError(f"Import response has no Location header: {response.status_code} {response.text}")
        return job_url

    def get_import_job(self, job_url):
        """
        Get import job status.

        :param job_url: as returned by import_github_repo
        :return: {"id":..., "status": "pending|complete|failed", "logs": [...]}
        """

        # Location header looks like https://app.snyk.io/api/v1/org/..., while requests go to server_address.
        path = urlparse(job_url).path
        path = path.removeprefix("/api")
        return self.get(path)

    def wait_for_import_job(self, job_url, timeout=600, sleep_time=10):
        """
        Poll the import job until it is not pending.

        :param job_url:
        :param timeout: seconds
        :param sleep_time: seconds
        :return: final job status dict
        """

        deadline = time.time() + timeout
        while True:
            job = self.get_import_job(job_url)
            status = job.get("status")
            logger.info(f"Import job {job.get('id')} status: {status}")
            if status != "pending":
                return job
            if time.time() > deadline:
                raise TimeoutError(f"Import job {job_url} still pending after {timeout} seconds")
            time.sleep(sleep_time)

    def import_github_repos(self, repos, org_id=None, integration_type="github-cloud-app", wait=True):
        """
        Import multiple GitHub repos.

        :param repos: list of "owner/name@branch"
        :param org_id:
        :param integration_type:
        :param wait: wait for every job to finish
        :return: {repo: job_url or final job dict}
        """

        ret = {}
        for repo in repos:
            if "@" not in repo:
                raise ValueError(f"Branch must be set explicitly: expected 'owner/name@branch', got '{repo}'")
            repo_path, branch = repo.split("@", 1)
            owner, name = repo_path.split("/", 1)
            ret[repo] = self.import_github_repo(owner, name, branch=branch, org_id=org_id,
                                                integration_type=integration_type)

        if wait:
            ret = {repo: self.wait_for_import_job(job_url) for repo, job_url in ret.items()}
        return ret
