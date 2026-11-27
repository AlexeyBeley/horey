"""
Discovers the installed horey packages and loads the MCP tools they expose.
"""

import importlib
import importlib.util
import pkgutil
from collections.abc import Callable
from pathlib import Path

from mcp.server.mcpserver import MCPServer

import horey
from horey.h_logger import get_logger
from horey.mcp.mcp_tools_registry import MCPToolsRegistry

logger = get_logger()


class MCPToolsLoader:
    """
    Main class.

    """

    MCP_TOOLS_MODULE_NAME: str = "mcp_tools"
    REGISTER_FUNCTION_NAME: str = "register_mcp_tools"

    def __init__(self, mcp_server: MCPServer, configurations_dir_path: str | Path | None,
                 packages: list[str] | None = None) -> None:
        """

        :param mcp_server:
        :param configurations_dir_path:
        :param packages: package names to load. None - all installed.
        """

        self.mcp_server: MCPServer = mcp_server
        self.configurations_dir_path: str | Path | None = configurations_dir_path
        self.packages: list[str] | None = packages
        self.loaded_packages: dict[str, list[str]] = {}
        self.failed_packages: dict[str, str] = {}

    @staticmethod
    def discover_packages() -> list[str]:
        """
        Names of the installed horey packages, e.g. ["github_api", "jenkins_api"].

        :return:
        """

        return sorted({name for _, name, is_package in pkgutil.iter_modules(horey.__path__) if is_package})

    def load(self) -> dict[str, list[str]]:
        """
        Register the tools of every package having horey.<package_name>.mcp_tools.
        A failing package is logged and skipped, it does not stop the server.

        :return: {package_name: [tool names]}
        """

        package_names = self.packages if self.packages is not None else self.discover_packages()
        for package_name in package_names:
            try:
                self.load_package(package_name)
            except Exception as error_inst:  # pylint: disable=broad-exception-caught
                logger.exception(f"Failed to load MCP tools of horey.{package_name}")
                self.failed_packages[package_name] = repr(error_inst)

        logger.info(f"Loaded MCP tools: {self.loaded_packages}")
        return self.loaded_packages

    def load_package(self, package_name: str) -> list[str] | None:
        """
        Register the tools of a single package.

        :param package_name:
        :return: list of tool names, None if the package does not expose tools.
        """

        module_name = f"horey.{package_name}.{self.MCP_TOOLS_MODULE_NAME}"
        try:
            spec = importlib.util.find_spec(module_name)
        except ModuleNotFoundError:
            spec = None

        if spec is None:
            if self.packages is not None:
                raise ModuleNotFoundError(f"{module_name} not found")
            return None

        module = importlib.import_module(module_name)
        register_function: Callable[[MCPToolsRegistry], None] | None = getattr(
            module, self.REGISTER_FUNCTION_NAME, None)
        if register_function is None:
            raise AttributeError(f"{module_name} has no {self.REGISTER_FUNCTION_NAME}(registry) function")

        registry = MCPToolsRegistry(self.mcp_server, package_name, self.configurations_dir_path,
                                    loaded_packages=self.loaded_packages)
        register_function(registry)
        self.loaded_packages[package_name] = registry.tool_names
        return registry.tool_names
