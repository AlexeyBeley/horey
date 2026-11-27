"""
MCP tools of horey.replacement_engine. Loaded by horey.mcp, see mcp/README.md.
Works on strings only: the server's file system is not the user's.
"""

from typing import TYPE_CHECKING

from horey.replacement_engine.replacement_engine import ReplacementEngine

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.tool(read_only=True)
    def render_template(template: str, string_replacements: dict[str, str],
                        cartesian_replacements: dict[str, list[str]] | None = None) -> str:
        """
        Render a horey template string. string_replacements keys must start with STRING_REPLACEMENT_,
        e.g. {"STRING_REPLACEMENT_NAME": "horey"}. Fails if a STRING_REPLACEMENT_ placeholder is left unresolved
        (unless cartesian_replacements are given). cartesian_replacements map a placeholder to a list of values.
        """
        return ReplacementEngine.perform_replacements_raw(template, string_replacements,
                                                          cartesian_replacements=cartesian_replacements)
