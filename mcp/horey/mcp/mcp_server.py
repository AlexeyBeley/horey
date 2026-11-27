"""
Horey MCP server: streamable HTTP MCP server exposing the tools of the installed horey packages.
"""

import argparse

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.server import TransportSecuritySettings

from horey.h_logger import get_logger
from horey.mcp import __version__
from horey.mcp.mcp_server_configuration_policy import MCPServerConfigurationPolicy
from horey.mcp.mcp_tools_loader import MCPToolsLoader

logger = get_logger()


class HoreyMCPServer:
    """
    Main class.

    """

    def __init__(self, configuration: MCPServerConfigurationPolicy | None = None) -> None:
        self.configuration: MCPServerConfigurationPolicy = configuration or MCPServerConfigurationPolicy()
        self.mcp_server: MCPServer = MCPServer(name=self.configuration.server_name, version=__version__)
        self.loader: MCPToolsLoader = MCPToolsLoader(self.mcp_server, self.configuration.configurations_dir_path,
                                                     packages=self.configuration.packages)

    def load_tools(self) -> dict[str, list[str]]:
        """
        Load the tools of the horey packages.

        :return:
        """

        return self.loader.load()

    @property
    def transport_security(self) -> TransportSecuritySettings:
        """
        DNS rebinding protection. Enabled explicitly: in a container the server binds 0.0.0.0,
        where the SDK does not enable it by itself.

        :return:
        """

        allowed_hosts = self.configuration.allowed_hosts
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=allowed_hosts,
            allowed_origins=[f"http://{host}" for host in allowed_hosts],
        )

    def run(self) -> None:
        """
        Load the tools and serve streamable HTTP.

        :return:
        """

        self.load_tools()
        logger.info(f"Serving MCP on http://{self.configuration.host}:{self.configuration.port}"
                    f"{self.configuration.streamable_http_path}")
        self.mcp_server.run(
            transport="streamable-http",
            host=self.configuration.host,
            port=self.configuration.port,
            streamable_http_path=self.configuration.streamable_http_path,
            transport_security=self.transport_security,
        )


def main() -> None:
    """
    Entry point. Configuration: --configuration_file_path, then HOREY_MCP_* environment variables.

    :return:
    """

    parser = argparse.ArgumentParser(description="Horey MCP server")
    parser.add_argument("--configuration_file_path", type=str, required=False)
    arguments = parser.parse_args()

    configuration = MCPServerConfigurationPolicy()
    if arguments.configuration_file_path:
        configuration.configuration_file_full_path = arguments.configuration_file_path
        configuration.init_from_file()
    configuration.init_from_environ()

    HoreyMCPServer(configuration).run()


if __name__ == "__main__":
    main()
