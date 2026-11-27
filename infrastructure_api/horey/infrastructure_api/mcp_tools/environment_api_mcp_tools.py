"""
MCP tools of horey.infrastructure_api EnvironmentAPI: read-only queries of the environment resources.
"""

from typing import Any

from horey.infrastructure_api.mcp_tools.base_mcp_tools import BaseMCPTools


class EnvironmentAPIMCPTools(BaseMCPTools):
    """
    EnvironmentAPI tools.
    """

    def register(self) -> None:
        """
        Register the tools.

        :return:
        """

        @self.registry.tool(read_only=True)
        def get_environment(configuration_name: str | None = None) -> dict[str, Any]:
            """Get the configured AWS environment (needs vpc_name in the configuration): region, VPC id and name, public and private subnet ids."""
            api = self.environment_api(configuration_name)
            return {"region": api.configuration.region, "vpc_id": api.vpc.id, "vpc_name": api.vpc.get_tagname(),
                    "public_subnets": [subnet.id for subnet in api.public_subnets],
                    "private_subnets": [subnet.id for subnet in api.private_subnets]}

        @self.registry.tool(read_only=True)
        def get_ecs_cluster(cluster_name: str, configuration_name: str | None = None) -> dict[str, Any]:
            """Get an ECS cluster of the environment: status, running/pending tasks, active services, capacity providers."""
            return self.registry.to_jsonable(self.environment_api(configuration_name).find_ecs_cluster(cluster_name))

        @self.registry.tool(read_only=True)
        def get_load_balancer(name: str, configuration_name: str | None = None) -> dict[str, Any]:
            """Get an application/network load balancer of the environment by name: DNS name, state, scheme, listeners."""
            return self.registry.to_jsonable(self.environment_api(configuration_name).get_load_balancer(name, full_information=True))

        @self.registry.tool(read_only=True)
        def get_load_balancer_target_groups(load_balancer_name: str, configuration_name: str | None = None) -> list[dict[str, Any]]:
            """Get the target groups of a load balancer with their targets' health."""
            target_groups = self.environment_api(configuration_name).get_load_balancers_target_groups(load_balancer_name, full_information=True)
            return self.registry.to_jsonable(target_groups)

        @self.registry.tool(read_only=True)
        def list_cloudwatch_alarms(state: str = "", configuration_name: str | None = None) -> list[dict[str, Any]]:
            """List the CloudWatch alarms in the environment region. state filters by OK, ALARM or INSUFFICIENT_DATA."""
            return [{"name": alarm.name, "state": alarm.state_value, "metric_name": alarm.metric_name,
                     "namespace": alarm.namespace, "state_updated": self.registry.to_jsonable(alarm.state_updated_timestamp),
                     "description": alarm.alarm_description}
                    for alarm in self.environment_api(configuration_name).get_cloudwatch_alarms() if not state or alarm.state_value == state]

        @self.registry.tool(read_only=True)
        def get_rds_cluster(cluster_id: str, configuration_name: str | None = None) -> dict[str, Any]:
            """Get an RDS DB cluster of the environment: status, engine and version, endpoints, members."""
            return self.registry.to_jsonable(self.environment_api(configuration_name).get_rds_cluster(cluster_id))
