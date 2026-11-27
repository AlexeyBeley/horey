"""
MCP tools of horey.grafana_api. Loaded by horey.mcp, see mcp/README.md.
"""

from typing import TYPE_CHECKING, Any

from horey.grafana_api.grafana_api import GrafanaAPI
from horey.grafana_api.grafana_api_configuration_policy import GrafanaAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def _title_and_uid(dict_src: dict[str, Any]) -> dict[str, Any]:
    """
    Dashboards and folders come from the Kubernetes style API: uid in metadata.name, title in spec.title.
    """

    metadata = dict_src.get("metadata") or {}
    spec = dict_src.get("spec") or {}
    annotations = metadata.get("annotations") or {}
    return {"uid": metadata.get("name"), "title": spec.get("title"),
            "folder_uid": annotations.get("grafana.app/folder")}


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def grafana_api(configuration_name: str | None) -> GrafanaAPI:
        return GrafanaAPI(registry.get_configuration(GrafanaAPIConfigurationPolicy, configuration_name))

    @registry.tool(read_only=True)
    def list_dashboards(title_contains: str = "", configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the Grafana dashboards: uid, title, folder uid. Optional title substring filter."""
        dashboards = [_title_and_uid(dashboard.dict_src) for dashboard in grafana_api(configuration_name).init_dashboards()]
        return [dashboard for dashboard in dashboards if title_contains.lower() in (dashboard["title"] or "").lower()]

    @registry.tool(read_only=True)
    def list_folders(configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the Grafana dashboard folders: uid, title, parent folder uid."""
        return [_title_and_uid(folder.dict_src) for folder in grafana_api(configuration_name).init_folders()]

    @registry.tool(read_only=True)
    def list_datasources(configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the Grafana data sources: uid, name, type, url, database, default. Credentials are not returned."""
        fields = ["id", "uid", "name", "type", "url", "database", "isDefault"]
        return [{field: datasource.dict_src.get(field) for field in fields}
                for datasource in grafana_api(configuration_name).init_datasources()]

    @registry.tool(read_only=True)
    def list_alert_rules(configuration_name: str | None = None) -> dict[str, list[dict[str, Any]]]:
        """List the Grafana managed alert rules per folder: group name, rule title, uid, paused."""
        api = grafana_api(configuration_name)
        api.init_rule_namespaces()
        ret = {}
        for namespace, groups in api.rule_namespaces.items():
            rules = []
            for group in groups:
                for rule in group.get("rules", []):
                    alert = rule.get("grafana_alert") or {}
                    rules.append({"group": group.get("name"), "title": alert.get("title"), "uid": alert.get("uid"),
                                  "paused": alert.get("is_paused")})
            ret[namespace] = rules
        return ret
