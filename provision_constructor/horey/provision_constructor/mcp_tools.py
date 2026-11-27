"""
MCP tools of horey.provision_constructor. Loaded by horey.mcp, see mcp/README.md.
System functions are provisioned on remote hosts over SSH, with horey.deployer
(add deployer to HOREY_MCP_PACKAGES). SSH keys are files in the MCP configurations directory, passed by file name.
"""

from typing import TYPE_CHECKING, Any

from horey.provision_constructor.provision_constructor import ProvisionConstructor
from horey.provision_constructor.system_function_factory import SystemFunctionFactory

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    def ssh_key_path(ssh_key_file_name: str) -> str:
        file_path = registry.get_configuration_file_path(file_name=ssh_key_file_name)
        if file_path is None:
            raise FileNotFoundError(f"SSH key {ssh_key_file_name} was not found in {registry.configurations_dir_path}")
        return file_path

    @registry.tool(read_only=True)
    def list_system_functions() -> list[str]:
        """List the system function names which can be provisioned, e.g. "docker", "logrotate", "zabbix"."""
        return sorted(SystemFunctionFactory.REGISTERED_FUNCTIONS)

    @registry.tool(destructive=True)
    def provision_system_function_remote(address: str, system_function_name: str, ssh_key_file_name: str,
                                         parameters: dict[str, Any] | None = None, user_name: str = "ubuntu",
                                         bastion_address: str | None = None,
                                         bastion_ssh_key_file_name: str | None = None,
                                         timeout_seconds: int = 60 * 60) -> Any:
        """
        Provision a system function (see list_system_functions) on a remote Linux host over SSH,
        e.g. install and configure a package. parameters are the system function's keyword arguments.
        """
        # pylint: disable= import-outside-toplevel
        from horey.deployer.deployment_target import DeploymentTarget
        from horey.deployer.remote_deployer import RemoteDeployer

        target = DeploymentTarget()
        target.deployment_target_address = address
        target.deployment_target_user_name = user_name
        target.deployment_target_ssh_key_path = ssh_key_path(ssh_key_file_name)
        if bastion_address:
            target.bastion_chain.append(DeploymentTarget.BastionChainLink(
                bastion_address, ssh_key_path(bastion_ssh_key_file_name or ssh_key_file_name), user_name=user_name))

        remoter = RemoteDeployer().get_remoter(target, default_timeout=timeout_seconds)
        provision_constructor = ProvisionConstructor()
        provision_constructor.deployment_dir = target.local_deployment_dir_path
        return registry.to_jsonable(provision_constructor.provision_system_function_remote(
            remoter, system_function_name, storage_service=None, **(parameters or {})))
