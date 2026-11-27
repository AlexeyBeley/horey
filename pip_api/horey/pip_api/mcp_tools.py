"""
MCP tools of horey.pip_api. Loaded by horey.mcp, see mcp/README.md.
The configuration files (pip_api_configuration[_<suffix>].py|json) are optional: venv_dir_path selects a venv,
default - the MCP server's own interpreter.
"""

from typing import TYPE_CHECKING, Any

from horey.pip_api.pip_api import PipAPI
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def pip_api(configuration_name: str | None) -> PipAPI:
        if configuration_name is None:
            configuration = PipAPIConfigurationPolicy()
        else:
            configuration = registry.get_configuration(PipAPIConfigurationPolicy, configuration_name)
        if configuration.multi_package_repositories is None:
            configuration.multi_package_repositories = {}
        return PipAPI(configuration)

    @registry.tool(read_only=True)
    def list_installed_packages(name_contains: str = "",
                                configuration_name: str | None = None) -> list[dict[str, Any]]:
        """
        List the installed Python packages (pip list) and their versions. Optional name substring filter.
        The list is read once per server run.
        """
        return [{"name": package.name, "version": package.version}
                for package in pip_api(configuration_name).init_packages() if name_contains.lower() in package.name.lower()]
