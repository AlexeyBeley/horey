"""
MCP tools of horey.snyk_api. Loaded by horey.mcp, see mcp/README.md.
org_id defaults to the configured one.
"""

from typing import TYPE_CHECKING, Any

from horey.snyk_api.snyk_api import SnykAPI
from horey.snyk_api.snyk_api_configuration_policy import SnykAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def _rest_item(item: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """
    Snyk REST items: {"id": ..., "attributes": {...}}.
    """

    attributes = item.get("attributes") or {}
    ret = {"id": item.get("id")}
    ret.update({field: attributes.get(field) for field in fields})
    return ret


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def snyk_api(configuration_name: str | None) -> SnykAPI:
        return SnykAPI(registry.get_configuration(SnykAPIConfigurationPolicy, configuration_name))

    @registry.tool(read_only=True)
    def list_orgs(configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the Snyk organisations accessible by the token: id, name, slug."""
        return [_rest_item(org, ["name", "slug"]) for org in snyk_api(configuration_name).get_orgs()]

    @registry.tool(read_only=True)
    def list_projects(org_id: str | None = None, name_contains: str = "",
                      configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the projects of a Snyk organisation: id, name, type, target file, branch, status."""
        projects = [_rest_item(project, ["name", "type", "target_file", "target_reference", "status"])
                    for project in snyk_api(configuration_name).get_projects(org_id=org_id)]
        return [project for project in projects if name_contains in (project["name"] or "")]

    @registry.tool(read_only=True)
    def list_targets(configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the targets (repositories) of the configured Snyk organisation: id, display name, url."""
        response = snyk_api(configuration_name).get_targets()
        return [_rest_item(target, ["display_name", "url"]) for target in response.get("data", [])]

    @registry.tool(read_only=True)
    def list_integrations(org_id: str | None = None, configuration_name: str | None = None) -> dict[str, str]:
        """List the integrations of a Snyk organisation: {integration type: integration id}."""
        return snyk_api(configuration_name).get_integrations(org_id=org_id)

    @registry.tool()
    def import_github_repo(owner: str, name: str, branch: str, org_id: str | None = None,
                           integration_type: str = "github-cloud-app", configuration_name: str | None = None) -> str:
        """
        Start importing a GitHub repository branch into a Snyk organisation and return without waiting.
        Returns the import job url: pass it to get_import_job.
        """
        return snyk_api(configuration_name).import_github_repo(owner, name, branch, org_id=org_id, integration_type=integration_type)

    @registry.tool(read_only=True)
    def get_import_job(job_url: str, configuration_name: str | None = None) -> dict[str, Any]:
        """Get a Snyk import job status (pending, complete, failed) and its logs."""
        return snyk_api(configuration_name).get_import_job(job_url)
