"""
MCP tools of horey.github_api. Loaded by horey.mcp, see mcp/README.md.
Repositories are in the organisation set by the configuration owner.
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.github_api.github_api import GithubAPI
from horey.github_api.github_api_configuration_policy import GithubAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry

WORKFLOW_RUN_FIELDS = ["id", "name", "path", "head_branch", "head_sha", "event", "status", "conclusion",
                       "run_number", "run_attempt", "created_at", "updated_at", "html_url"]
JOB_FIELDS = ["id", "name", "status", "conclusion", "started_at", "completed_at", "runner_name", "html_url"]


def _pick(src: Any, fields: list[str]) -> dict[str, Any]:
    """
    Selected fields of a dict or an object.
    """

    if isinstance(src, dict):
        return {field: src.get(field) for field in fields}
    return {field: getattr(src, field, None) for field in fields}


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def github_api() -> GithubAPI:
        return GithubAPI(registry.get_configuration(GithubAPIConfigurationPolicy))

    def owner() -> str:
        return github_api().configuration.owner

    @registry.tool(read_only=True)
    def list_repositories(include_archived: bool = False) -> list[dict[str, Any]]:
        """List the repositories of the configured GitHub organisation: name, default branch, visibility, archived."""
        repositories = github_api().init_repositories()
        return [_pick(repository, ["name", "default_branch", "visibility", "archived"])
                for repository in repositories if include_archived or not repository.get("archived")]

    @registry.tool(read_only=True)
    def list_workflows(repo_name: str) -> list[dict[str, Any]]:
        """List the GitHub Actions workflows of a repository: id, name, path (the file to pass as workflow_file), state."""
        return [_pick(workflow.dict_src, ["id", "name", "path", "state"])
                for workflow in github_api().get_repository_workflows(repo_name)]

    @registry.tool(read_only=True)
    def list_workflow_runs(repo_name: str, workflow_file: str | None = None, branch_name: str = "",
                           created_after: str = "", limit: int = 20) -> list[dict[str, Any]]:
        """
        List recent workflow runs of a repository, newest first.
        workflow_file filters by the workflow file, e.g. "build.yml". created_after: ISO time, e.g. "2026-01-01T00:00:00Z".
        """
        runs = github_api().get_workflow_runs(repo_name, action_name=workflow_file or "", created_after=created_after,
                                              branch_name=branch_name)
        return [_pick(run, WORKFLOW_RUN_FIELDS) for run in runs[:limit]]

    @registry.tool(read_only=True)
    def get_workflow_run(repo_name: str, run_id: int) -> dict[str, Any]:
        """Get the status, conclusion and the jobs of a workflow run."""
        run = github_api().get(f"repos/{owner()}/{repo_name}/actions/runs/{run_id}")
        jobs = github_api().get(f"repos/{owner()}/{repo_name}/actions/runs/{run_id}/jobs")
        ret = _pick(run, WORKFLOW_RUN_FIELDS)
        ret["jobs"] = [_pick(job, JOB_FIELDS) for job in jobs.get("jobs", [])]
        return ret

    @registry.tool()
    def trigger_workflow(repo_name: str, workflow_file: str, branch_name: str,
                         inputs: dict[str, str] | None = None) -> str:
        """
        Trigger a workflow_dispatch workflow on a branch and return without waiting.
        workflow_file: the workflow file name, e.g. "build.yml". Find the run with list_workflow_runs.
        """
        parameters: dict[str, Any] = {"inputs": inputs} if inputs else {}
        github_api().trigger_action(f"{owner()}/{repo_name}", workflow_file, branch_name,
                                    asynchronous=True, parameters=parameters)
        return f"Triggered {workflow_file} on {repo_name}:{branch_name}"

    @registry.tool(read_only=True)
    def get_branch_rules(repo_name: str, branch_name: str) -> list[dict[str, Any]]:
        """Get all the rules active on a branch, from the repository and the organisation rulesets."""
        return github_api().get_branch_rules(repo_name, branch_name)

    @registry.tool(read_only=True)
    def get_branch_required_status_checks(repo_name: str, branch_name: str) -> list[str]:
        """Get the required status check names enforced by rulesets on a branch."""
        return github_api().get_branch_required_status_checks(repo_name, branch_name)

    @registry.tool(read_only=True)
    def get_repository_direct_teams(repo_name: str) -> list[dict[str, Any]]:
        """List the teams with direct access to a repository (not through organisation level access)."""
        return [_pick(team, ["name", "slug", "permission"]) for team in github_api().get_repository_direct_teams(repo_name)]

    @registry.tool(read_only=True)
    def list_repository_runners(repo_name: str) -> list[dict[str, Any]]:
        """List the self-hosted runners of a repository: name, status, busy, labels."""
        return [{"id": runner.get("id"), "name": runner.get("name"), "status": runner.get("status"),
                 "busy": runner.get("busy"), "labels": [label.get("name") for label in runner.get("labels", [])]}
                for runner in github_api().init_repository_self_hosted_runners(repo_name)]
