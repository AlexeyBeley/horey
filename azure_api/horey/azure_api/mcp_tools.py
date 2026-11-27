"""
MCP tools of horey.azure_api. Loaded by horey.mcp, see mcp/README.md.
The configuration file (azure_api_configuration.py|json) sets accounts_file and azure_account.
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.azure_api.azure_api import AzureAPI
from horey.azure_api.azure_api_configuration_policy import AzureAPIConfigurationPolicy

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def _pick(src: Any, fields: list[str]) -> dict[str, Any]:
    return {field: getattr(src, field, None) for field in fields}


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def azure_api() -> AzureAPI:
        return AzureAPI(registry.get_configuration(AzureAPIConfigurationPolicy))

    @registry.tool(read_only=True)
    def list_resource_groups() -> list[dict[str, Any]]:
        """List the Azure resource groups of the configured account: name, location, tags."""
        return [_pick(resource_group, ["name", "location", "tags"])
                for resource_group in azure_api().resource_client.get_all_resource_groups()]

    @registry.tool(read_only=True)
    def list_virtual_machines(resource_group_name: str) -> list[dict[str, Any]]:
        """List the virtual machines of an Azure resource group: name, location, size, provisioning state, zones."""
        ret = []
        for virtual_machine in azure_api().compute_client.get_all_virtual_machines(resource_group_name):
            vm_dict = _pick(virtual_machine, ["name", "location", "provisioning_state", "zones", "tags"])
            vm_dict["vm_size"] = (virtual_machine.hardware_profile or {}).get("vm_size")
            ret.append(vm_dict)
        return ret

    @registry.tool(read_only=True)
    def list_public_ip_addresses(resource_group_name: str) -> list[dict[str, Any]]:
        """List the public IP addresses of an Azure resource group: name, address, allocation method, attached to."""
        ret = []
        for address in azure_api().network_client.get_all_public_ip_addresses(None, resource_group_name=resource_group_name):
            address_dict = _pick(address, ["name", "ip_address", "public_ip_allocation_method", "location"])
            address_dict["ip_configuration_id"] = (address.ip_configuration or {}).get("id")
            ret.append(address_dict)
        return ret
