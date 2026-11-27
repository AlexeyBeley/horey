"""
MCP tools of the horey.mcp package itself. Loaded like any other horey package's mcp_tools.
"""

from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: MCPToolsRegistry) -> None:
    """
    Register the tools.

    :param registry: horey.mcp.mcp_tools_registry.MCPToolsRegistry
    :return:
    """

    @registry.tool(read_only=True)
    def list_packages() -> dict[str, list[str]]:
        """List the horey packages loaded into this MCP server and the tools each one exposes."""
        return dict(registry.loaded_packages)
