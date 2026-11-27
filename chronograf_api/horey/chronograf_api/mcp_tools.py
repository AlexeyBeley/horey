"""
MCP tools of horey.chronograf_api. Loaded by horey.mcp, see mcp/README.md.
"""

from typing import TYPE_CHECKING, Any

from horey.chronograf_api.chronograf_api import ChronografAPI
from horey.chronograf_api.chronograf_api_configuration_policy import ChronografAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def _pick(dict_src: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: dict_src.get(field) for field in fields}


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def chronograf_api(configuration_name: str | None) -> ChronografAPI:
        return ChronografAPI(registry.get_configuration(ChronografAPIConfigurationPolicy, configuration_name))

    @registry.tool(read_only=True)
    def list_sources(configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the Chronograf data sources (InfluxDB connections): id, name, url, type, default."""
        api = chronograf_api(configuration_name)
        api.init_sources()
        return [_pick(source.dict_src, ["id", "name", "url", "type", "default"]) for source in api.sources]

    @registry.tool(read_only=True)
    def list_kapacitors(configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the Kapacitor connections of all Chronograf sources: id, name, url, active."""
        api = chronograf_api(configuration_name)
        api.init_kapacitors()
        return [_pick(kapacitor.dict_src, ["id", "name", "url", "active"]) for kapacitor in api.kapacitors]

    @registry.tool(read_only=True)
    def list_alert_rules(name_contains: str = "", configuration_name: str | None = None) -> list[dict[str, Any]]:
        """List the Kapacitor alert rules of all Chronograf sources: id, name, status, trigger, message."""
        api = chronograf_api(configuration_name)
        api.init_rules()
        return [_pick(rule.dict_src, ["id", "name", "status", "trigger", "message"])
                for rule in api.rules if name_contains in (rule.dict_src.get("name") or "")]
