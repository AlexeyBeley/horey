"""
Base of the horey.infrastructure_api MCP tools classes.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from horey.infrastructure_api.environment_api import EnvironmentAPI

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


class BaseMCPTools:
    """
    Registers the tools of one infrastructure_api API class.
    AWS is accessed only through the infrastructure_api classes, never through horey.aws_api directly.
    """

    def __init__(self, registry: "MCPToolsRegistry",
                 environment_api: Callable[[str | None], EnvironmentAPI]) -> None:
        """

        :param registry: passed in by horey.mcp
        :param environment_api: configuration name to its EnvironmentAPI, shared by all the tools classes:
            a single EnvironmentAPI (and AWS account) per configuration.
        """

        self.registry = registry
        self.environment_api = environment_api

    def register(self) -> None:
        """
        Register the tools.

        :return:
        """

        raise NotImplementedError(f"{type(self).__name__}.register")
