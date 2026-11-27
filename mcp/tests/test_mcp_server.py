"""
Testing horey MCP server
"""

import asyncio
import datetime
import json
from pathlib import Path
from typing import Any

import pytest
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import CallToolResult, TextContent

from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.mcp.mcp_server import HoreyMCPServer
from horey.mcp.mcp_server_configuration_policy import MCPServerConfigurationPolicy
from horey.mcp.mcp_tools_loader import MCPToolsLoader
from horey.mcp.mcp_tools_registry import MCPToolsRegistry

# pylint: disable= missing-function-docstring

FAKE_MCP_TOOLS = '''
def register_mcp_tools(registry) -> None:
    @registry.tool(read_only=True)
    def get_status(name: str) -> dict:
        """Get the status."""
        return {"name": name, "configuration": registry.get_configuration_file_path()}
'''


@pytest.fixture(name="fake_package")
def fixture_fake_package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    horey.horey_fake_api exposing a single tool, with its configuration file.
    """

    package_dir_path = tmp_path / "horey" / "horey_fake_api"
    package_dir_path.mkdir(parents=True)
    (package_dir_path / "__init__.py").write_text("")
    (package_dir_path / "mcp_tools.py").write_text(FAKE_MCP_TOOLS)

    configurations_dir_path = tmp_path / "configurations"
    configurations_dir_path.mkdir()
    (configurations_dir_path / "horey_fake_api_configuration.json").write_text("{}")

    monkeypatch.syspath_prepend(str(tmp_path))
    return configurations_dir_path


def make_server(configurations_dir_path: Path, packages: list[str] | str | None = None) -> HoreyMCPServer:
    configuration = MCPServerConfigurationPolicy()
    configuration.configurations_dir_path = str(configurations_dir_path)
    configuration.packages = packages
    return HoreyMCPServer(configuration)


@pytest.mark.unit
def test_discover_packages(fake_package: Path) -> None:
    assert fake_package
    packages = MCPToolsLoader.discover_packages()
    assert "horey_fake_api" in packages
    assert "mcp" in packages


@pytest.mark.unit
def test_load_tools(fake_package: Path) -> None:
    server = make_server(fake_package)
    loaded = server.load_tools()
    assert loaded["horey_fake_api"] == ["horey_fake_api_get_status"]
    assert loaded["mcp"] == ["mcp_list_packages"]

    tool_names = [tool.name for tool in asyncio.run(server.mcp_server.list_tools())]
    assert "horey_fake_api_get_status" in tool_names


@pytest.mark.unit
def test_call_tool(fake_package: Path) -> None:
    server = make_server(fake_package, packages="horey_fake_api")
    server.load_tools()
    result = asyncio.run(server.mcp_server.call_tool("horey_fake_api_get_status", {"name": "repo-horey"}))
    assert isinstance(result, CallToolResult)
    assert not result.is_error
    content = result.content[0]
    assert isinstance(content, TextContent)
    status = json.loads(content.text)
    assert status["name"] == "repo-horey"
    assert status["configuration"].endswith("horey_fake_api_configuration.json")


@pytest.mark.unit
def test_missing_requested_package_is_skipped(fake_package: Path) -> None:
    server = make_server(fake_package, packages=["horey_missing_api", "horey_fake_api"])
    loaded = server.load_tools()
    assert list(loaded) == ["horey_fake_api"]
    assert "horey_missing_api" in server.loader.failed_packages


FAILING_MCP_TOOLS = '''
def register_mcp_tools(registry):
    @registry.tool()
    def fail() -> str:
        """Always fails."""
        raise ValueError("repo-horey is broken")
'''


@pytest.mark.unit
def test_tool_error_text_reaches_client(fake_package: Path) -> None:
    package_dir_path = fake_package.parent / "horey" / "horey_failing_api"
    package_dir_path.mkdir()
    (package_dir_path / "__init__.py").write_text("")
    (package_dir_path / "mcp_tools.py").write_text(FAILING_MCP_TOOLS)

    server = make_server(fake_package, packages="horey_failing_api")
    server.load_tools()
    with pytest.raises(ToolError, match="ValueError: repo-horey is broken"):
        asyncio.run(server.mcp_server.call_tool("horey_failing_api_fail", {}))


class HoreyConfigurationPolicy(ConfigurationPolicy):
    """
    Configuration with a single attribute.
    """

    def __init__(self) -> None:
        super().__init__()
        self._name: str | None = None

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value


@pytest.mark.unit
def test_get_configuration(tmp_path: Path) -> None:
    (tmp_path / "horey_fake_api_configuration.json").write_text('{"name": "repo-horey"}')
    registry = MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", tmp_path)
    assert registry.get_configuration(HoreyConfigurationPolicy).name == "repo-horey"


@pytest.mark.unit
def test_get_configuration_missing(tmp_path: Path) -> None:
    registry = MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", tmp_path)
    with pytest.raises(FileNotFoundError, match="horey_fake_api_configuration"):
        registry.get_configuration(HoreyConfigurationPolicy)


MULTI_CONFIGURATION_MCP_TOOLS = '''
from horey.configuration_policy.configuration_policy import ConfigurationPolicy


class HoreyConfigurationPolicy(ConfigurationPolicy):
    def __init__(self):
        super().__init__()
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


def register_mcp_tools(registry) -> None:
    @registry.cached_per_configuration
    def api(configuration_name):
        return registry.get_configuration(HoreyConfigurationPolicy, configuration_name)

    @registry.tool(read_only=True)
    def get_name(configuration_name: str | None = None) -> str:
        """Get the configured name."""
        return api(configuration_name).name
'''


@pytest.fixture(name="multi_configuration_package")
def fixture_multi_configuration_package(fake_package: Path) -> Path:
    """
    horey.horey_multi_api with dev and production configurations.
    """

    package_dir_path = fake_package.parent / "horey" / "horey_multi_api"
    package_dir_path.mkdir()
    (package_dir_path / "__init__.py").write_text("")
    (package_dir_path / "mcp_tools.py").write_text(MULTI_CONFIGURATION_MCP_TOOLS)
    (fake_package / "horey_multi_api_configuration_dev_horey.json").write_text('{"name": "dev-horey"}')
    (fake_package / "horey_multi_api_configuration_production_horey.json").write_text('{"name": "production-horey"}')
    return fake_package


def call_tool_text(server: HoreyMCPServer, tool_name: str, arguments: dict[str, Any]) -> str:
    result = asyncio.run(server.mcp_server.call_tool(tool_name, arguments))
    assert isinstance(result, CallToolResult)
    assert not result.is_error
    content = result.content[0]
    assert isinstance(content, TextContent)
    return content.text


@pytest.mark.unit
def test_list_configurations(tmp_path: Path) -> None:
    for file_name in ["horey_fake_api_configuration.py", "horey_fake_api_configuration_dev_horey.json",
                      "horey_fake_api_configurationx_horey.json", "horey_fake_api_configuration_dev_horey.txt",
                      "horey_fake_api_x_configuration.json", "horey_fake_api_horey_configuration.json"]:
        (tmp_path / file_name).write_text("{}")
    (tmp_path / "horey_fake_api_configuration_dir_horey.json").mkdir()
    registry = MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", tmp_path)
    assert registry.list_configurations() == ["horey_fake_api_configuration.py",
                                              "horey_fake_api_configuration_dev_horey.json"]


@pytest.mark.unit
def test_list_configurations_no_directory(tmp_path: Path) -> None:
    assert not MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", tmp_path / "missing").list_configurations()
    assert not MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", None).list_configurations()


@pytest.mark.unit
def test_resolve_configuration_name(tmp_path: Path) -> None:
    registry = MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", tmp_path)
    assert registry.resolve_configuration_name(None) is None

    (tmp_path / "horey_fake_api_configuration_dev_horey.json").write_text("{}")
    assert registry.resolve_configuration_name(None) == "horey_fake_api_configuration_dev_horey.json"

    (tmp_path / "horey_fake_api_configuration_production_horey.json").write_text("{}")
    with pytest.raises(ValueError, match="pass configuration_name.*production_horey"):
        registry.resolve_configuration_name(None)
    assert (registry.resolve_configuration_name("horey_fake_api_configuration_production_horey.json")
            == "horey_fake_api_configuration_production_horey.json")
    with pytest.raises(ValueError, match="Unknown"):
        registry.resolve_configuration_name("horey_fake_api_configuration_staging_horey.json")


@pytest.mark.unit
def test_get_configuration_by_name(tmp_path: Path) -> None:
    (tmp_path / "horey_fake_api_configuration_dev_horey.json").write_text('{"name": "dev-horey"}')
    (tmp_path / "horey_fake_api_configuration_production_horey.json").write_text('{"name": "production-horey"}')
    registry = MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", tmp_path)
    assert registry.get_configuration(HoreyConfigurationPolicy,
                                      "horey_fake_api_configuration_dev_horey.json").name == "dev-horey"
    with pytest.raises(ValueError, match="pass configuration_name"):
        registry.get_configuration(HoreyConfigurationPolicy)


@pytest.mark.unit
def test_cached_per_configuration(tmp_path: Path) -> None:
    (tmp_path / "horey_fake_api_configuration_dev_horey.json").write_text("{}")
    registry = MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", tmp_path)
    built: list[str | None] = []

    @registry.cached_per_configuration
    def api(configuration_name: str | None) -> object:
        built.append(configuration_name)
        return object()

    # None resolves to the only configuration: the same object as the explicit name.
    assert api(None) is api("horey_fake_api_configuration_dev_horey.json")
    (tmp_path / "horey_fake_api_configuration_production_horey.json").write_text("{}")
    assert api("horey_fake_api_configuration_production_horey.json") is not api(
        "horey_fake_api_configuration_dev_horey.json")
    assert built == ["horey_fake_api_configuration_dev_horey.json",
                     "horey_fake_api_configuration_production_horey.json"]


@pytest.mark.unit
def test_list_configurations_tool_registered_once(tmp_path: Path) -> None:
    mcp_server = MCPServer("horey")
    registry = MCPToolsRegistry(mcp_server, "horey_fake_api", tmp_path)

    @registry.tool(read_only=True)
    def get_status() -> str:
        """Get the status."""
        return "ok"

    assert registry.tool_names == ["horey_fake_api_get_status"]

    @registry.tool(read_only=True)
    def get_first(configuration_name: str | None = None) -> str | None:
        """Get the first."""
        return configuration_name

    @registry.tool(read_only=True)
    def get_second(configuration_name: str | None = None) -> str | None:
        """Get the second."""
        return configuration_name

    assert registry.tool_names == ["horey_fake_api_get_status", "horey_fake_api_list_configurations",
                                   "horey_fake_api_get_first", "horey_fake_api_get_second"]
    tools = {tool.name: tool for tool in asyncio.run(mcp_server.list_tools())}
    assert "horey_fake_api_list_configurations" in (tools["horey_fake_api_get_first"].description or "")
    assert "list_configurations" not in (tools["horey_fake_api_get_status"].description or "")


@pytest.mark.unit
def test_multi_configuration_tools(multi_configuration_package: Path) -> None:
    server = make_server(multi_configuration_package, packages="horey_multi_api")
    loaded = server.load_tools()
    assert loaded["horey_multi_api"] == ["horey_multi_api_list_configurations", "horey_multi_api_get_name"]

    result = asyncio.run(server.mcp_server.call_tool("horey_multi_api_list_configurations", {}))
    assert isinstance(result, CallToolResult)
    assert result.structured_content == {"result": ["horey_multi_api_configuration_dev_horey.json",
                              "horey_multi_api_configuration_production_horey.json"]}

    assert call_tool_text(server, "horey_multi_api_get_name",
                          {"configuration_name": "horey_multi_api_configuration_dev_horey.json"}) == "dev-horey"
    assert call_tool_text(server, "horey_multi_api_get_name",
                          {"configuration_name": "horey_multi_api_configuration_production_horey.json"}
                          ) == "production-horey"
    with pytest.raises(ToolError, match="ValueError: There are 2 horey_multi_api configurations"):
        asyncio.run(server.mcp_server.call_tool("horey_multi_api_get_name", {}))


@pytest.mark.unit
def test_server_instructions(fake_package: Path) -> None:
    assert "list_configurations" in (make_server(fake_package).mcp_server.instructions or "")


@pytest.mark.unit
def test_get_configuration_file_path_rejects_paths(tmp_path: Path) -> None:
    (tmp_path / "ssh_key_horey").write_text("")
    registry = MCPToolsRegistry(MCPServer("horey"), "horey_fake_api", tmp_path / "configurations")
    (tmp_path / "configurations").mkdir()
    for file_name in ["../ssh_key_horey", "/etc/hosts", "..", "."]:
        with pytest.raises(ValueError, match="File name expected"):
            registry.get_configuration_file_path(file_name=file_name)
    assert registry.get_configuration_file_path(file_name="missing_horey") is None


class HoreyObject:
    """
    Object with public, private and nested attributes.
    """

    def __init__(self) -> None:
        self.name = "repo-horey"
        self._region = "region-horey"
        self.created = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        self.path = Path("/opt/horey")
        self.children = [{"dict_src_horey": 1}]


class HoreyApiObject:
    """
    Object initialized from an API response.
    """

    def __init__(self) -> None:
        self.dict_src = {"id": "id-horey"}
        self.id = "id-horey"


@pytest.mark.unit
def test_to_jsonable() -> None:
    assert MCPToolsRegistry.to_jsonable(HoreyObject()) == {
        "name": "repo-horey", "region": "region-horey", "created": "2026-01-01T00:00:00+00:00",
        "path": "/opt/horey", "children": [{"dict_src_horey": 1}]}
    assert MCPToolsRegistry.to_jsonable(HoreyApiObject()) == {"id": "id-horey"}
    assert MCPToolsRegistry.to_jsonable({"nested": {"deeper": 1}}, max_depth=1) == {"nested": "{'deeper': 1}"}
