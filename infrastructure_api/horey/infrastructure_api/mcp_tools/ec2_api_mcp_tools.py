"""
MCP tools of horey.infrastructure_api EC2API: EC2 instances and security groups of the environment VPC.
The tools changing them are not read-only.
"""

import datetime
from typing import Any

from horey.infrastructure_api.ec2_api import EC2API
from horey.infrastructure_api.ec2_api_configuration_policy import EC2APIConfigurationPolicy
from horey.infrastructure_api.infrastructure_api import InfrastructureAPI
from horey.infrastructure_api.mcp_tools.base_mcp_tools import BaseMCPTools


def ec2_instance_summary(ec2_instance: Any) -> dict[str, Any]:
    """
    The fields of an EC2Instance needed to work with it.
    """

    placement = getattr(ec2_instance, "placement", None) or {}
    launch_time = getattr(ec2_instance, "launch_time", None)
    return {"id": getattr(ec2_instance, "id", None), "name": ec2_instance.get_tagname(ignore_missing_tag=True),
            "state": (getattr(ec2_instance, "state", None) or {}).get("Name"),
            "instance_type": ec2_instance.instance_type, "private_ip_address": ec2_instance.private_ip_address,
            "public_ip_address": ec2_instance.public_ip_address, "private_dns_name": ec2_instance.private_dns_name,
            "subnet_id": ec2_instance.subnet_id, "availability_zone": placement.get("AvailabilityZone"),
            "image_id": ec2_instance.image_id, "key_name": ec2_instance.key_name,
            "security_groups": [{"id": group.get("GroupId"), "name": group.get("GroupName")}
                                for group in ec2_instance.security_groups or []],
            "launch_time": launch_time.isoformat() if isinstance(launch_time, datetime.datetime) else launch_time}


def ip_permission_summary(permission: dict[str, Any]) -> dict[str, Any]:
    """
    A security group rule: protocol, ports and the sources (CIDRs, prefix lists, security groups) with descriptions.
    """

    return {"protocol": "all" if permission.get("IpProtocol") == "-1" else permission.get("IpProtocol"),
            "from_port": permission.get("FromPort"), "to_port": permission.get("ToPort"),
            "cidrs": [{"cidr": ip_range.get("CidrIp"), "description": ip_range.get("Description")}
                      for ip_range in permission.get("IpRanges", [])]
                     + [{"cidr": ip_range.get("CidrIpv6"), "description": ip_range.get("Description")}
                        for ip_range in permission.get("Ipv6Ranges", [])],
            "prefix_lists": [prefix_list.get("PrefixListId") for prefix_list in permission.get("PrefixListIds", [])],
            "security_groups": [{"id": pair.get("GroupId"), "description": pair.get("Description")}
                                for pair in permission.get("UserIdGroupPairs", [])]}


def security_group_summary(security_group: Any) -> dict[str, Any]:
    """
    The fields of an EC2SecurityGroup: id, name, description, VPC and the rules.
    """

    return {"id": getattr(security_group, "id", None), "name": security_group.name,
            "description": security_group.description, "vpc_id": security_group.vpc_id,
            "ingress": [ip_permission_summary(permission) for permission in security_group.ip_permissions or []],
            "egress": [ip_permission_summary(permission)
                       for permission in security_group.ip_permissions_egress or []]}


class EC2APIMCPTools(BaseMCPTools):
    """
    EC2API tools.
    """

    def ec2_api(self, configuration_name: str | None) -> EC2API:
        """
        EC2API of the configuration environment.
        """

        return InfrastructureAPI.get_ec2_api(EC2APIConfigurationPolicy(), self.environment_api(configuration_name))

    # pylint: disable= too-many-arguments, too-many-positional-arguments
    def register(self) -> None:
        """
        Register the tools.

        :return:
        """

        @self.registry.tool(read_only=True)
        def ec2_list_instances(name: str = "", tags: dict[str, list[str]] | None = None, states: list[str] | None = None,
                               configuration_name: str | None = None) -> list[dict[str, Any]]:
            """
            List the EC2 instances of the environment VPC (needs vpc_name in the configuration): id, name, state, type,
            IPs, subnet, availability zone, image, key, security groups, launch time.
            name: Name tag value, "*" wildcards allowed, e.g. "*-runner". tags: {"tag name": ["values"]}.
            states: e.g. ["running", "stopped"]; terminated instances are listed by AWS for about an hour.
            """
            tags_dict = dict(tags or {})
            if name:
                tags_dict["Name"] = [name]
            instances = [ec2_instance_summary(instance)
                         for instance in self.ec2_api(configuration_name).get_instances(tags_dict=tags_dict)]
            return [instance for instance in instances if not states or instance["state"] in states]

        @self.registry.tool(read_only=True)
        def ec2_get_instance(name: str, configuration_name: str | None = None) -> dict[str, Any]:
            """Get the EC2 instance of the environment VPC by its Name tag. Fails unless exactly one matches."""
            return ec2_instance_summary(self.ec2_api(configuration_name).get_instance(name=name))

        @self.registry.tool(read_only=True)
        def ec2_get_security_group(name: str = "", group_id: str = "",
                                   configuration_name: str | None = None) -> dict[str, Any]:
            """
            Get a security group of the environment VPC by name or id: description and the ingress and egress rules
            (protocol, ports, source CIDRs, prefix lists and security groups with descriptions).
            """
            if bool(name) == bool(group_id):
                raise ValueError("Pass name or group_id")
            return security_group_summary(self.ec2_api(configuration_name).get_security_group(name=name or None,
                                                                                         group_id=group_id or None))

        @self.registry.tool(read_only=True)
        def ec2_get_ubuntu_24_04_image(architecture: str = "amd64",
                                       configuration_name: str | None = None) -> dict[str, Any]:
            """Get the latest Canonical Ubuntu 24.04 AMI of the environment region. architecture: amd64 or arm64."""
            ami = self.ec2_api(configuration_name).get_ubuntu24_04_image(architecture=architecture)
            return {"id": ami.id, "name": getattr(ami, "name", None),
                    "creation_date": self.registry.to_jsonable(getattr(ami, "creation_date", None)),
                    "architecture": architecture}

        @self.registry.tool(read_only=True)
        def ec2_get_private_subnets_offering_instance_type(instance_type: str,
                                                           configuration_name: str | None = None) -> list[dict[str, Any]]:
            """List the environment private subnets whose availability zone offers an instance type, e.g. "t3a.small"."""
            api = self.ec2_api(configuration_name)
            subnets = api.choose_subnets_with_instance_type_offerings(instance_type, api.environment_api.private_subnets)
            return [{"id": subnet.id, "availability_zone": subnet.availability_zone, "cidr_block": subnet.cidr_block}
                    for subnet in subnets]

        @self.registry.tool(idempotent=True)
        def ec2_start_instance(name: str, configuration_name: str | None = None) -> dict[str, Any]:
            """Start the EC2 instance with this Name tag and wait until it runs (about a minute). Running - no change."""
            return ec2_instance_summary(self.ec2_api(configuration_name).start_instance(name=name))

        @self.registry.tool(destructive=True, idempotent=True)
        def ec2_stop_instance(name: str, wait: bool = False, configuration_name: str | None = None) -> dict[str, Any]:
            """
            Stop (force) the EC2 instance with this Name tag. Returns right away unless wait: check the state with
            ec2_get_instance. Instance store data is lost.
            """
            return ec2_instance_summary(self.ec2_api(configuration_name).stop_instance(name=name, asynchronous=not wait))

        @self.registry.tool(destructive=True)
        def ec2_dispose_instance(name: str, missing_ok: bool = True, configuration_name: str | None = None) -> str:
            """
            Terminate the EC2 instance with this Name tag. Irreversible: the instance and its delete-on-termination
            volumes are deleted. missing_ok: no instance - success.
            """
            self.ec2_api(configuration_name).dispose_instance(name=name, missing_ok=missing_ok)
            return f"Instance {name} terminated (or did not exist)"

        @self.registry.tool(idempotent=True)
        def ec2_provision_security_group(name: str, description: str = "",
                                         configuration_name: str | None = None) -> dict[str, Any]:
            """
            Create a security group in the environment VPC, tagged with the environment tags, if it does not exist.
            Its rules are not changed: add them with ec2_security_group_add_rule.
            """
            api = self.ec2_api(configuration_name)
            api.provision_security_group(name=name, description=description or None)
            return security_group_summary(api.get_security_group(name=name))

        @self.registry.tool(idempotent=True)
        def ec2_provision_alb_security_group(public: bool = False,
                                             configuration_name: str | None = None) -> dict[str, Any]:
            """
            Create the environment internal (private) or external (public) ALB security group if it does not exist.
            Needs environment_level and environment_name in the configuration.
            """
            api = self.ec2_api(configuration_name)
            security_group = api.provision_public_alb_security_group() if public else \
                api.provision_private_alb_security_group()
            return security_group_summary(api.get_security_group(name=security_group.name))

        @self.registry.tool(idempotent=True)
        def ec2_security_group_add_rule(security_group_name: str, source_security_group_id: str, from_port: int,
                                        to_port: int | None = None,
                                        configuration_name: str | None = None) -> dict[str, Any]:
            """
            Allow TCP from_port..to_port (default: from_port) into a security group of the environment VPC from another
            security group (source_security_group_id, e.g. "sg-0123"). Existing rule - no change.
            Returns the updated group.
            """
            api = self.ec2_api(configuration_name)
            api.security_group_add_rule(api.get_security_group(name=security_group_name),
                                        source_group=source_security_group_id,
                                        port_range=[from_port, from_port if to_port is None else to_port])
            return security_group_summary(api.get_security_group(name=security_group_name))

        @self.registry.tool(idempotent=True)
        def ec2_provision_ssh_key(name: str, configuration_name: str | None = None) -> dict[str, Any]:
            """
            Create an ed25519 EC2 key pair if it does not exist. The private key is saved to Secrets Manager
            in the environment region, as a secret named like the key: download it with download_secret_file.
            """
            key_pair = self.ec2_api(configuration_name).provision_ssh_key(name)
            return {"name": key_pair.name, "id": getattr(key_pair, "id", None), "key_type": key_pair.key_type,
                    "private_key_secret_name": key_pair.name}

        @self.registry.tool()
        def ec2_provision_ubuntu_24_04_instance(name: str, security_group_names: list[str], instance_type: str = "",
                                                architecture: str = "amd64", volume_size: int = 30, key_name: str = "",
                                                wait: bool = False,
                                                configuration_name: str | None = None) -> dict[str, Any]:
            """
            Create an Ubuntu 24.04 EC2 instance in an environment private subnet (no public IP), tagged Name=name,
            unless a running or pending instance with this name exists. Costs money while it runs.
            security_group_names: of the environment VPC. instance_type: default t3a.medium (amd64), t4g.medium (arm64).
            key_name: default - a new key "key_<name>", its private key saved to Secrets Manager.
            volume_size: root gp3 volume GB. wait: until the instance runs (minutes), else return right away.
            """
            api = self.ec2_api(configuration_name)
            security_groups = [api.get_security_group(name=group_name) for group_name in security_group_names]
            ec2_instance = api.provision_ubuntu_24_04_instance(name, security_groups=security_groups,
                                                               volume_size=volume_size, key_name=key_name or None,
                                                               instance_type=instance_type or None,
                                                               architecture=architecture, asynchronous=not wait)
            return ec2_instance_summary(ec2_instance)
