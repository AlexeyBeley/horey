"""
MCP tools of horey.infrastructure_api. Loaded by horey.mcp, see mcp/README.md.

Read-only queries of a single AWS environment. The configuration file
(infrastructure_api_configuration.py|json) holds the EnvironmentAPIConfigurationPolicy values, at least region.
AWS credentials come from the standard AWS environment (variables, profile or role).
"""

import functools
from typing import TYPE_CHECKING, Any

from horey.aws_api.aws_api import AWSAPI
from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.infrastructure_api.environment_api_configuration_policy import EnvironmentAPIConfigurationPolicy
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI

if TYPE_CHECKING:
    from horey.mcp.mcp_tools_registry import MCPToolsRegistry


def register_mcp_tools(registry: "MCPToolsRegistry") -> None:
    """
    Register the tools.

    :param registry: passed in by horey.mcp
    """

    @functools.cache
    def environment_api() -> EnvironmentAPI:
        configuration = registry.get_configuration(EnvironmentAPIConfigurationPolicy)
        return InfrastructureAPI().get_environment_api(configuration, AWSAPI())

    @registry.tool(read_only=True)
    def get_environment() -> dict[str, Any]:
        """Get the configured AWS environment (needs vpc_name in the configuration): region, VPC id and name, public and private subnet ids."""
        api = environment_api()
        return {"region": api.configuration.region, "vpc_id": api.vpc.id, "vpc_name": api.vpc.get_tagname(),
                "public_subnets": [subnet.id for subnet in api.public_subnets],
                "private_subnets": [subnet.id for subnet in api.private_subnets]}

    @registry.tool(read_only=True)
    def get_ecs_cluster(cluster_name: str) -> dict[str, Any]:
        """Get an ECS cluster of the environment: status, running/pending tasks, active services, capacity providers."""
        return registry.to_jsonable(environment_api().find_ecs_cluster(cluster_name))

    @registry.tool(read_only=True)
    def get_load_balancer(name: str) -> dict[str, Any]:
        """Get an application/network load balancer of the environment by name: DNS name, state, scheme, listeners."""
        return registry.to_jsonable(environment_api().get_load_balancer(name, full_information=True))

    @registry.tool(read_only=True)
    def get_load_balancer_target_groups(load_balancer_name: str) -> list[dict[str, Any]]:
        """Get the target groups of a load balancer with their targets' health."""
        target_groups = environment_api().get_load_balancers_target_groups(load_balancer_name, full_information=True)
        return registry.to_jsonable(target_groups)

    @registry.tool(read_only=True)
    def list_cloudwatch_alarms(state: str = "") -> list[dict[str, Any]]:
        """List the CloudWatch alarms in the environment region. state filters by OK, ALARM or INSUFFICIENT_DATA."""
        return [{"name": alarm.name, "state": alarm.state_value, "metric_name": alarm.metric_name,
                 "namespace": alarm.namespace, "state_updated": registry.to_jsonable(alarm.state_updated_timestamp),
                 "description": alarm.alarm_description}
                for alarm in environment_api().get_cloudwatch_alarms() if not state or alarm.state_value == state]

    @registry.tool(read_only=True)
    def get_rds_cluster(cluster_id: str) -> dict[str, Any]:
        """Get an RDS DB cluster of the environment: status, engine and version, endpoints, members."""
        return registry.to_jsonable(environment_api().get_rds_cluster(cluster_id))

    @registry.tool(read_only=True)
    def get_cloudwatch_log_group(log_group_name: str) -> dict[str, Any]:
        """Get a CloudWatch log group: retention, stored bytes, creation time."""
        return registry.to_jsonable(environment_api().get_cloudwatch_log_group(log_group_name))
