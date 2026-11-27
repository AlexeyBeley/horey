"""
MCP tools of horey.git_api. Loaded by horey.mcp, see mcp/README.md.
Works on the single repository set by the configuration file (git_api_configuration.py|json):
remote_address, directory_path (the local clone), main_branch_name and ssh_key_file_path or user and pat.
"""

from typing import TYPE_CHECKING, Any

from horey.git_api.git_api import GitAPI
from horey.git_api.git_api_configuration_policy import GitAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def git_api(configuration_name: str | None) -> GitAPI:
        return GitAPI(registry.get_configuration(GitAPIConfigurationPolicy, configuration_name))

    @registry.tool(read_only=True)
    def get_repository(configuration_name: str | None = None) -> dict[str, Any]:
        """Get the configured repository: remote address, local directory, main branch and the checked out commit."""
        api = git_api(configuration_name)
        cloned = api.configuration.directory_path.exists()
        return {"remote_address": api.configuration.remote_address,
                "directory_path": str(api.configuration.directory_path),
                "main_branch_name": api.configuration.main_branch_name,
                "cloned": cloned,
                "commit_id": api.get_commit_id() if cloned else None}

    @registry.tool(destructive=True)
    def checkout_remote(branch_name: str | None = None, configuration_name: str | None = None) -> dict[str, Any]:
        """
        Clone the repository if needed, fetch and check out a remote branch (default: the main branch)
        or a pull request: "refs/pull/<number>/head". The clone is reset hard: local changes are discarded.
        Returns the checked out commit.
        """
        api = git_api(configuration_name)
        api.checkout_remote(dst_obj=branch_name)
        return {"checked_out": branch_name or api.configuration.main_branch_name, "commit_id": api.get_commit_id()}
