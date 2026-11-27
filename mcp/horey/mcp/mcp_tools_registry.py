"""
Registry handed to a horey package to register its MCP tools.

A horey package exposes tools by adding a module horey/<package_name>/mcp_tools.py with:

    def register_mcp_tools(registry):
        @registry.tool(read_only=True)
        def get_build_status(job_name: str, build_number: int) -> dict:
            \"\"\"Get the status of a Jenkins build.\"\"\"
            ...

The package does not import horey.mcp, the registry is passed in.
"""

import datetime
import enum
import functools
import inspect
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


class MCPToolsRegistry:
    """
    Main class.

    """

    CONFIGURATION_FILE_EXTENSIONS: list[str] = [".py", ".json"]

    def __init__(self, mcp_server: MCPServer, package_name: str, configurations_dir_path: str | Path | None,
                 loaded_packages: dict[str, list[str]] | None = None) -> None:
        self.mcp_server: MCPServer = mcp_server
        self.package_name: str = package_name
        self.configurations_dir_path: Path | None = Path(configurations_dir_path) if configurations_dir_path else None
        self.loaded_packages: dict[str, list[str]] = loaded_packages if loaded_packages is not None else {}
        self.tool_names: list[str] = []

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
            annotations = ToolAnnotations(
                read_only_hint=read_only,
                destructive_hint=False if read_only else destructive,
                idempotent_hint=True if read_only else idempotent,
            )
            self.mcp_server.add_tool(self.report_errors(func), name=tool_name, description=description,
                                     annotations=annotations)
            self.tool_names.append(tool_name)
            return func

        return decorator

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
                          file_name: str | None = None) -> ConfigurationType:
        """
        Create a configuration policy and init it from the package configuration file.

        :param configuration_class: e.g. JenkinsAPIConfigurationPolicy
        :param file_name: Default: <package_name>_configuration.py or <package_name>_configuration.json.
        :return:
        """

        file_path = self.get_configuration_file_path(file_name=file_name)
        if file_path is None:
            expected = file_name or f"{self.package_name}_configuration.py|.json"
            raise FileNotFoundError(f"Configuration file {expected} was not found in {self.configurations_dir_path}")

        configuration = configuration_class()
        configuration.configuration_file_full_path = file_path
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
        Find the package configuration file in the configurations directory.

        :param file_name: Default: <package_name>_configuration.py or <package_name>_configuration.json.
        :return: str or None if it does not exist.
        """

        if self.configurations_dir_path is None:
            return None

        file_names = [file_name] if file_name else [f"{self.package_name}_configuration{extension}"
                                                    for extension in self.CONFIGURATION_FILE_EXTENSIONS]
        for file_name_tmp in file_names:
            file_path = self.configurations_dir_path / file_name_tmp
            if file_path.is_file():
                return str(file_path)
        return None
