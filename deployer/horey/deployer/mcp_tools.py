"""
MCP tools of horey.deployer. Loaded by horey.mcp, see mcp/README.md.
No configuration file. SSH keys are files in the horey MCP configurations directory, passed by file name.
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.deployer.deployment_target import DeploymentTarget
from horey.deployer.remote_deployer import RemoteDeployer

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def remote_deployer() -> RemoteDeployer:
        return RemoteDeployer()

    def ssh_key_path(ssh_key_file_name: str) -> str:
        file_path = registry.get_configuration_file_path(file_name=ssh_key_file_name)
        if file_path is None:
            raise FileNotFoundError(f"SSH key {ssh_key_file_name} was not found in {registry.configurations_dir_path}")
        return file_path

    @registry.tool(destructive=True)
    def run_remote_command(address: str, command: str, ssh_key_file_name: str, user_name: str = "ubuntu",
                           port: int = 22, bastion_address: str | None = None,
                           bastion_ssh_key_file_name: str | None = None, bastion_user_name: str = "ubuntu",
                           timeout_seconds: int = 300, tail_lines: int = 200) -> dict[str, Any]:
        """
        Run a shell command on a remote Linux host over SSH, optionally through a bastion host.
        ssh_key_file_name: a private key file in the MCP configurations directory.
        Fails if the command exits with a non-zero status. Returns the exit status and the last output lines.
        """
        target = DeploymentTarget()
        target.deployment_target_address = address
        target.deployment_target_user_name = user_name
        target.deployment_target_ssh_key_path = ssh_key_path(ssh_key_file_name)
        target.deployment_target_ssh_port = port
        if bastion_address:
            target.bastion_chain.append(DeploymentTarget.BastionChainLink(
                bastion_address, ssh_key_path(bastion_ssh_key_file_name or ssh_key_file_name),
                user_name=bastion_user_name))

        deployer = remote_deployer()
        channel = deployer.get_deployment_target_ssh_client(target).invoke_shell()
        _, shout, _, exit_status = deployer.execute_remote_shell(channel, command, address,
                                                                 timeout=timeout_seconds)
        return {"exit_status": exit_status, "output": [str(line) for line in shout[-tail_lines:]]}
