"""
MCP tools of horey.opensearch_api. Loaded by horey.mcp, see mcp/README.md.
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.opensearch_api.opensearch_api import OpensearchAPI
from horey.opensearch_api.opensearch_api_configuration_policy import OpensearchAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def opensearch_api() -> OpensearchAPI:
        return OpensearchAPI(registry.get_configuration(OpensearchAPIConfigurationPolicy))

    @registry.tool(read_only=True)
    def get_cluster_health() -> dict[str, Any]:
        """Get the OpenSearch cluster health: status (green/yellow/red), nodes, shards."""
        return opensearch_api().get("_cluster/health")

    @registry.tool(read_only=True)
    def list_indices(pattern: str = "*") -> list[dict[str, Any]]:
        """List the indices matching a pattern: name, health, status, documents count, size."""
        indices = opensearch_api().get(f"_cat/indices/{pattern}?format=json&bytes=b&s=index")
        return [{"index": index.get("index"), "health": index.get("health"), "status": index.get("status"),
                 "docs_count": index.get("docs.count"), "size_bytes": index.get("store.size")} for index in indices]

    @registry.tool(read_only=True)
    def list_monitors() -> list[dict[str, Any]]:
        """List the alerting monitors: id, name, type, enabled, schedule, trigger names."""
        api = opensearch_api()
        api.init_monitors()
        return [{"id": monitor.id, "name": monitor.name, "monitor_type": monitor.monitor_type,
                 "enabled": monitor.enabled, "schedule": monitor.schedule,
                 "triggers": [registry.to_jsonable(trigger) for trigger in monitor.triggers or []]}
                for monitor in api.monitors]

    @registry.tool(read_only=True)
    def list_index_management_policies() -> list[dict[str, Any]]:
        """List the index state management (ISM) policies: id, description, default state, states, index patterns."""
        api = opensearch_api()
        api.init_index_management_policies()
        return [{"id": policy.id, "description": policy.description, "default_state": policy.default_state,
                 "states": [(state or {}).get("name") for state in policy.states or []],
                 "ism_template": registry.to_jsonable(policy.ism_template)}
                for policy in api.index_management_policies]

    @registry.tool(read_only=True)
    def list_index_templates() -> list[dict[str, Any]]:
        """List the composable index templates: name, index patterns, priority."""
        templates = opensearch_api().get("_index_template").get("index_templates", [])
        return [{"name": template.get("name"),
                 "index_patterns": (template.get("index_template") or {}).get("index_patterns"),
                 "priority": (template.get("index_template") or {}).get("priority")} for template in templates]

    @registry.tool(read_only=True)
    def list_notification_channels() -> list[dict[str, Any]]:
        """List the notification channels: id, name, type, enabled."""
        return [{"id": channel.get("config_id"), "name": channel.get("name"), "type": channel.get("config_type"),
                 "enabled": channel.get("is_enabled")} for channel in opensearch_api().init_notification_channels()]
