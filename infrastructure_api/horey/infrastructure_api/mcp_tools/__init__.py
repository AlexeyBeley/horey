"""
MCP tools of horey.infrastructure_api. Loaded by horey.mcp, see mcp/README.md.

Queries and management of AWS environments. Each configuration file
(infrastructure_api_configuration[_<suffix>].py|json) is an environment: the EnvironmentAPIConfigurationPolicy
values, at least region. Each environment gets its own AWSAccount, so environments in different regions
are served by the same server. AWS credentials come from the standard AWS environment (variables, profile or role).

The tools are grouped by the API class they use, one module per class:

* environment_api_mcp_tools.EnvironmentAPIMCPTools - environment, ECS, load balancers, alarms, RDS
* secrets_api_mcp_tools.SecretsAPIMCPTools - Secrets Manager secrets
* cloudwatch_api_mcp_tools.CloudwatchAPIMCPTools - CloudWatch Logs
* ec2_api_mcp_tools.EC2APIMCPTools - EC2 instances and security groups
* cicd_api_mcp_tools.CICDAPIMCPTools - provision_constructor system functions run on EC2 instances

A new module is added to MCP_TOOLS_CLASSES explicitly: the classes are imported statically.
"""

from typing import TYPE_CHECKING

from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.mcp_tools.base_mcp_tools import BaseMCPTools
from horey.infrastructure_api.mcp_tools.cicd_api_mcp_tools import CICDAPIMCPTools
from horey.infrastructure_api.mcp_tools.cloudwatch_api_mcp_tools import CloudwatchAPIMCPTools
from horey.infrastructure_api.mcp_tools.ec2_api_mcp_tools import EC2APIMCPTools
from horey.infrastructure_api.mcp_tools.environment_api_mcp_tools import EnvironmentAPIMCPTools
from horey.infrastructure_api.mcp_tools.secrets_api_mcp_tools import SecretsAPIMCPTools

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry

MCP_TOOLS_CLASSES: list[type[BaseMCPTools]] = [EnvironmentAPIMCPTools, SecretsAPIMCPTools, CloudwatchAPIMCPTools,
                                               EC2APIMCPTools, CICDAPIMCPTools]


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools of all the MCP_TOOLS_CLASSES.

    :param registry: passed in by horey.mcp
    """

    @registry.cached_per_configuration
    def environment_api(configuration_name: str | None) -> EnvironmentAPI:
        configuration = registry.get_configuration(EnvironmentAPIConfigurationPolicy, configuration_name)
        return InfrastructureAPI.get_isolated_environment_api(configuration, configuration_name)

    for mcp_tools_class in MCP_TOOLS_CLASSES:
        mcp_tools_class(registry, environment_api).register()
