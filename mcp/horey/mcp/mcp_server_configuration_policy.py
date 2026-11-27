"""
MCP server configuration policy
"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy

#pylint: disable= missing-function-docstring


class MCPServerConfigurationPolicy(ConfigurationPolicy):
    """
    Main class.

    Environment variables are prefixed with HOREY_MCP_, e.g. HOREY_MCP_PORT=8080,
    HOREY_MCP_PACKAGES=jenkins_api,github_api.
    """

    ENVIRON_ATTRIBUTE_PREFIX: str = "horey_mcp_"

    def __init__(self) -> None:
        super().__init__()
        self._server_name: str = "horey"
        self._host: str = "127.0.0.1"
        self._port: int = 8080
        self._streamable_http_path: str = "/mcp"
        self._configurations_dir_path: str = "/opt/horey/mcp/configurations"
        self._packages: list[str] | None = None
        self._allowed_hosts: list[str] = ["127.0.0.1:*", "localhost:*", "[::1]:*"]

    @property
    def server_name(self) -> str:
        return self._server_name

    @server_name.setter
    def server_name(self, value: str) -> None:
        self._server_name = value

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        self._host = value

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int | str) -> None:
        self._port = int(value)

    @property
    def streamable_http_path(self) -> str:
        return self._streamable_http_path

    @streamable_http_path.setter
    def streamable_http_path(self, value: str) -> None:
        self._streamable_http_path = value

    @property
    def configurations_dir_path(self) -> str:
        """
        Directory holding the horey packages' configuration files,
        named <package_name>_configuration.py or <package_name>_configuration.json.

        :return:
        """

        return self._configurations_dir_path

    @configurations_dir_path.setter
    def configurations_dir_path(self, value: str) -> None:
        self._configurations_dir_path = value

    @property
    def packages(self) -> list[str] | None:
        """
        Horey packages to load the tools from, e.g. ["jenkins_api", "github_api"].
        None - every installed horey package exposing tools.

        :return:
        """

        return self._packages

    @packages.setter
    def packages(self, value: list[str] | str | None) -> None:
        # Empty (e.g. HOREY_MCP_PACKAGES="") means all packages.
        self._packages = self._to_list(value) or None

    @property
    def allowed_hosts(self) -> list[str]:
        """
        Host header values accepted by the server (DNS rebinding protection).

        :return:
        """

        return self._allowed_hosts

    @allowed_hosts.setter
    def allowed_hosts(self, value: list[str] | str) -> None:
        self._allowed_hosts = self._to_list(value) or []

    @staticmethod
    def _to_list(value: list[str] | str | None) -> list[str] | None:
        """
        Lists can come from environment variables as comma separated strings.

        :param value:
        :return:
        """

        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value
