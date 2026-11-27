"""
MCP tools of horey.infrastructure_api SecretsAPI: AWS Secrets Manager secrets, read in the configuration
secrets_manager_region (default: region).
"""

import os
import tempfile
from pathlib import Path
from typing import Any

from horey.infrastructure_api.mcp_tools.base_mcp_tools import BaseMCPTools
from horey.infrastructure_api.secrets_api import SecretsAPI
from horey.infrastructure_api.secrets_api_configuration_policy import SecretsAPIConfigurationPolicy


def write_private_file(file_path: Path, contents: str, overwrite: bool = False) -> None:
    """
    Write a file readable by its owner only (0600), atomically: a temporary file in the same directory,
    created 0600, replaces the destination. The contents are never readable by others, even partially.

    :param file_path: absolute path.
    :param contents:
    :param overwrite: replace an existing file.
    :return:
    """

    if not file_path.is_absolute():
        raise ValueError(f"Absolute file path expected: {file_path}")
    if file_path.is_dir():
        raise IsADirectoryError(f"{file_path} is a directory")
    if file_path.exists() and not overwrite:
        raise FileExistsError(f"{file_path} exists, pass overwrite=True to replace it")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, tmp_file_path = tempfile.mkstemp(dir=file_path.parent, prefix=f".{file_path.name}.")
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as file_handler:
            file_handler.write(contents)
            file_handler.flush()
            os.fsync(file_handler.fileno())
        os.replace(tmp_file_path, file_path)
    except BaseException:
        Path(tmp_file_path).unlink(missing_ok=True)
        raise


class SecretsAPIMCPTools(BaseMCPTools):
    """
    SecretsAPI tools.
    """

    def secrets_api(self, configuration_name: str | None, region: str | None) -> SecretsAPI:
        """
        SecretsAPI of the configuration environment, reading in region (default: the secrets region).
        """

        api = self.environment_api(configuration_name)
        secrets_api_configuration = SecretsAPIConfigurationPolicy()
        secrets_api_configuration.region = region or api.configuration.secrets_manager_region
        return SecretsAPI(secrets_api_configuration, api)

    def register(self) -> None:
        """
        Register the tools.

        :return:
        """

        @self.registry.tool(read_only=True)
        def get_secret(secret_name: str, region: str | None = None,
                       configuration_name: str | None = None) -> dict[str, Any]:
            """
            Read an AWS Secrets Manager secret string. The value is returned in the result, i.e. it becomes part of
            the conversation: use download_secret_file when the value only has to reach a file.
            region: default - the environment secrets region.
            """
            api = self.secrets_api(configuration_name, region)
            return {"secret_name": secret_name, "region": api.region.region_mark, "value": api.get_secret(secret_name)}

        @self.registry.tool(destructive=True)
        def download_secret_file(secret_name: str, file_path: str, overwrite: bool = False, region: str | None = None,
                                 configuration_name: str | None = None) -> dict[str, Any]:
            """
            Download an AWS Secrets Manager secret string to a file, readable by its owner only (0600).
            The value is not returned. file_path: absolute, on the host running the MCP server (inside the container
            when the server runs in docker). Missing directories are created. An existing file is replaced only with
            overwrite. region: default - the environment secrets region.
            """
            destination = Path(file_path).expanduser()
            if not destination.is_absolute():
                raise ValueError(f"Absolute file path expected: {file_path}")
            if destination.exists() and not overwrite:
                raise FileExistsError(f"{destination} exists, pass overwrite=True to replace it")

            api = self.secrets_api(configuration_name, region)
            contents = api.get_secret(secret_name)
            write_private_file(destination, contents, overwrite=overwrite)
            return {"secret_name": secret_name, "region": api.region.region_mark, "file_path": str(destination),
                    "size_bytes": destination.stat().st_size}
