"""
Registry handed to a horey package to register its MCP tools.

A horey package exposes tools by adding a module horey/<package_name>/mcp_tools.py with:

    def register_mcp_tools(registry):
        @registry.tool(read_only=True)
        def get_build_status(job_name: str, build_number: int) -> dict:
            \"\"\"Get the status of a Jenkins build.\"\"\"
            ...

The package does not import horey.mcp, the registry is passed in.

A package can have several configurations (e.g. dev, staging and production Jenkins servers): files named
<package_name>_configuration[_<suffix>].py|json in the configurations directory. Tools select one with
the configuration_name parameter, a file name from the <package_name>_list_configurations tool:

    def register_mcp_tools(registry):
        @registry.cached_per_configuration
        def jenkins_api(configuration_name: str | None) -> JenkinsAPI:
            return JenkinsAPI(registry.get_configuration(JenkinsAPIConfigurationPolicy, configuration_name))

        @registry.tool(read_only=True)
        def list_jobs(configuration_name: str | None = None) -> list:
            \"\"\"List the Jenkins jobs.\"\"\"
            return jenkins_api(configuration_name).get_all_jobs()
"""

import datetime
import enum
import functools
import inspect
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from horey.configuration_policy.configuration_policy import ConfigurationPolicy
from horey.h_logger import get_logger

logger = get_logger()

ToolFunction = TypeVar("ToolFunction", bound=Callable[..., Any])
ConfigurationType = TypeVar("ConfigurationType", bound=ConfigurationPolicy)
ApiType = TypeVar("ApiType")


class MCPToolsRegistry:
    """
    Main class.

    """

    CONFIGURATION_FILE_EXTENSIONS: list[str] = [".py", ".json"]
    CONFIGURATION_NAME_PARAMETER: str = "configuration_name"

    def __init__(self, mcp_server: MCPServer, package_name: str, configurations_dir_path: str | Path | None,
                 loaded_packages: dict[str, list[str]] | None = None) -> None:
        self.mcp_server: MCPServer = mcp_server
        self.package_name: str = package_name
        self.configurations_dir_path: Path | None = Path(configurations_dir_path) if configurations_dir_path else None
        self.loaded_packages: dict[str, list[str]] = loaded_packages if loaded_packages is not None else {}
        self.tool_names: list[str] = []
        self._list_configurations_registered: bool = False

    def tool(self, name: str | None = None, description: str | None = None, read_only: bool = False,
             destructive: bool | None = None, idempotent: bool | None = None
             ) -> Callable[[ToolFunction], ToolFunction]:
        """
        Decorator registering a function as an MCP tool named <package_name>_<name>.
        The docstring is the tool description, the type hints are the input schema.

        :param name: tool name without the package prefix. Default: the function name.
        :param description: Default: the function docstring.
        :param read_only: the tool does not change anything.
        :param destructive: the tool may delete or overwrite.
        :param idempotent: calling the tool again with the same arguments has no additional effect.
        :return:
        """

        def decorator(func: ToolFunction) -> ToolFunction:
            tool_name = f"{self.package_name}_{name or func.__name__}"
            tool_description = description
            if self.CONFIGURATION_NAME_PARAMETER in inspect.signature(func).parameters:
                tool_description = (f"{(description or inspect.getdoc(func) or '').strip()}\n"
                                    f"{self.CONFIGURATION_NAME_PARAMETER}: a configuration file name from "
                                    f"{self.package_name}_list_configurations. Optional when only one exists.")
                self.register_list_configurations_tool()
            annotations = ToolAnnotations(
                read_only_hint=read_only,
                destructive_hint=False if read_only else destructive,
                idempotent_hint=True if read_only else idempotent,
            )
            self.mcp_server.add_tool(self.report_errors(func), name=tool_name, description=tool_description,
                                     annotations=annotations)
            self.tool_names.append(tool_name)
            return func

        return decorator

    def register_list_configurations_tool(self) -> None:
        """
        Register <package_name>_list_configurations. Called on the first tool having a configuration_name parameter.

        :return:
        """

        if self._list_configurations_registered:
            return
        self._list_configurations_registered = True

        @self.tool(name="list_configurations", read_only=True)
        def list_configurations() -> list[str]:
            """
            List the configuration file names of this package. Each one is a separate environment or server
            (e.g. development, staging, production) described by its name: pass it as configuration_name
            to the other tools of this package. If it is not clear which one the user means, ask.
            """
            return self.list_configurations()

    def list_configurations(self) -> list[str]:
        """
        File names of <package_name>_configuration[_<suffix>].py|json in the configurations directory.

        :return:
        """

        if self.configurations_dir_path is None or not self.configurations_dir_path.is_dir():
            return []

        prefix = f"{self.package_name}_configuration"
        return sorted(file_path.name for file_path in self.configurations_dir_path.iterdir()
                      if file_path.is_file() and file_path.name.startswith(prefix)
                      and file_path.suffix in self.CONFIGURATION_FILE_EXTENSIONS
                      and file_path.stem[len(prefix):len(prefix) + 1] in ("", "_"))

    def resolve_configuration_name(self, configuration_name: str | None) -> str | None:
        """
        The given configuration name if it exists, or the only one when not given.

        :param configuration_name: a file name from list_configurations.
        :return: None if the package has no configurations.
        """

        configuration_names = self.list_configurations()
        if configuration_name is not None:
            if configuration_name not in configuration_names:
                raise ValueError(f"Unknown {self.package_name} configuration {configuration_name!r}, "
                                 f"available: {configuration_names}")
            return configuration_name

        if len(configuration_names) > 1:
            raise ValueError(f"There are {len(configuration_names)} {self.package_name} configurations, "
                             f"pass {self.CONFIGURATION_NAME_PARAMETER}, one of: {configuration_names}")
        return configuration_names[0] if configuration_names else None

    def cached_per_configuration(self, build: Callable[[str | None], ApiType]) -> Callable[[str | None], ApiType]:
        """
        Decorator replacing functools.cache for API objects: one object per configuration.
        build receives the resolved configuration name, None if the package has no configurations.

        :param build:
        :return:
        """

        cache: dict[str | None, ApiType] = {}
        lock = threading.Lock()

        @functools.wraps(build)
        def wrapper(configuration_name: str | None = None) -> ApiType:
            resolved_name = self.resolve_configuration_name(configuration_name)
            with lock:
                if resolved_name not in cache:
                    cache[resolved_name] = build(resolved_name)
                return cache[resolved_name]

        return wrapper

    @staticmethod
    def report_errors(func: ToolFunction) -> ToolFunction:
        """
        Re-raise the tool exceptions as ToolError: the MCP SDK returns only "Error executing tool <name>"
        for other exceptions, the error text is what tells Claude what went wrong.
        functools.wraps keeps the signature, the input schema is generated from it.

        :param func:
        :return:
        """

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await func(*args, **kwargs)
                except ToolError:
                    raise
                except Exception as error_inst:
                    logger.exception(f"Tool {func.__name__} failed")
                    raise ToolError(f"{type(error_inst).__name__}: {error_inst}") from error_inst
            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ToolError:
                raise
            except Exception as error_inst:
                logger.exception(f"Tool {func.__name__} failed")
                raise ToolError(f"{type(error_inst).__name__}: {error_inst}") from error_inst
        return wrapper  # type: ignore[return-value]

    def get_configuration(self, configuration_class: type[ConfigurationType],
                          configuration_name: str | None = None) -> ConfigurationType:
        """
        Create a configuration policy and init it from a package configuration file.

        :param configuration_class: e.g. JenkinsAPIConfigurationPolicy
        :param configuration_name: a file name from list_configurations. Default: the only one.
        :return:
        """

        resolved_name = self.resolve_configuration_name(configuration_name)
        if resolved_name is None:
            raise FileNotFoundError(f"Configuration file {self.package_name}_configuration[_<suffix>].py|.json "
                                    f"was not found in {self.configurations_dir_path}")

        configuration = configuration_class()
        configuration.configuration_file_full_path = str(self.configurations_dir_path / resolved_name)
        configuration.init_from_file()
        return configuration

    @classmethod
    def to_jsonable(cls, obj: Any, max_depth: int = 6) -> Any:
        """
        Convert horey objects to JSON serializable values for tool results.
        Objects with dict_src return it (the raw API response), others - their public attributes.

        :param obj:
        :param max_depth: nested objects deeper than that are returned as str.
        :return:
        """

        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, enum.Enum):
            return cls.to_jsonable(obj.value, max_depth)
        if isinstance(obj, (Path, bytes)):
            return str(obj)
        if max_depth <= 0:
            return str(obj)
        if isinstance(obj, dict):
            return {str(key): cls.to_jsonable(value, max_depth - 1) for key, value in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [cls.to_jsonable(value, max_depth - 1) for value in obj]

        dict_src = getattr(obj, "dict_src", None)
        if isinstance(dict_src, dict):
            return cls.to_jsonable(dict_src, max_depth - 1)

        attributes = getattr(obj, "__dict__", None)
        if attributes is None:
            return str(obj)
        return {key.lstrip("_"): cls.to_jsonable(value, max_depth - 1) for key, value in attributes.items()
                if not key.startswith("__") and not callable(value)}

    def get_configuration_file_path(self, file_name: str | None = None) -> str | None:
        """
        Find a file (e.g. an SSH key) or the package configuration file in the configurations directory.

        :param file_name: a file name, not a path. Default: the only package configuration file.
        :return: str or None if it does not exist.
        """

        if self.configurations_dir_path is None:
            return None

        if file_name is None:
            resolved_name = self.resolve_configuration_name(None)
            return str(self.configurations_dir_path / resolved_name) if resolved_name else None

        if Path(file_name).name != file_name or file_name in (".", ".."):
            raise ValueError(f"File name expected, not a path: {file_name!r}")

        file_path = self.configurations_dir_path / file_name
        return str(file_path) if file_path.is_file() else None
