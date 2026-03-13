"""
Standard EC2 maintainer.

"""
from typing import Union

from horey.aws_api.aws_services_entities.key_pair import KeyPair
from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup
from horey.infrastructure_api.ec2_api_configuration_policy import EC2APIConfigurationPolicy
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
logger = get_logger()


class EC2API:
    """
    Manage ECS.

    """

    def __init__(self, configuration: EC2APIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def get_instance(self, name=None, update_info=True, tags_dict=None):
        """
        Get instnace.

        :param name:
        :return:
        """

        if tags_dict is None:
            if name is None:
                raise ValueError("tags_dict and name are None")
            tags_dict = {"Name": [name]}

        for tag_name, tag_value in tags_dict.items():
            if not isinstance(tag_value, list):
                raise ValueError(f"Tag '{tag_name}' value is not list: '{tag_value}'")

        filters = {"Filters": [{"Name": f"tag:{name}", "Values": values} for name, values in tags_dict.items()] +
                              [{"Name": "vpc-id", "Values": [self.environment_api.vpc.id]}]
                   }
        ec2_instances = self.environment_api.aws_api.ec2_client.get_region_instances(self.environment_api.region, filters=filters,
                                                                     update_info=update_info)
        if len(ec2_instances) != 1:
            raise RuntimeError(f"Expected to find single instance, found: {len(ec2_instances)}")
        return ec2_instances[0]

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """

        self.provision_security_group()

    def provision_security_group(self, name=None, description=None):
        """
        Provision log group.

        :param description:
        :param name:
        :return:
        """

        if not name:
            logger.error("Security group Name was not set, this is old style code")

        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.environment_api.vpc.id
        security_group.name = name or self.configuration.name
        security_group.description = description or security_group.name
        security_group.region = self.environment_api.region
        security_group.tags = self.environment_api.configuration.tags
        security_group.tags.append({
            "Key": "Name",
            "Value": security_group.name
        })

        self.environment_api.aws_api.provision_security_group(security_group, provision_rules=False)

        return security_group

    def get_security_group(self, name=None):
        """
        Get security group.

        :param name:
        :return:
        """

        filters = {"Filters": [
            {"Name": "vpc-id", "Values": [self.environment_api.vpc.id]},
            {"Name": "group-name", "Values": [name]}
        ]}
        security_groups = self.environment_api.aws_api.ec2_client.get_region_security_groups(self.environment_api.region,
                                                                                             filters=filters)
        if len(security_groups) != 1:
            raise RuntimeError(f"Expected to find single security group, found: {len(security_groups)}")
        return security_groups[0]

    def get_ubuntu24_04_image(self):
        """
        Get latest Ubuntu24.04 image in this region.

        :return:
        """

        param = self.environment_api.aws_api.ssm_client.get_region_parameter(self.environment_api.region,
                                                             "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id")

        filter_request = {"ImageIds": [param.value]}
        amis = self.environment_api.aws_api.ec2_client.get_region_amis(self.environment_api.region, custom_filters=filter_request)
        if len(amis) != 1:
            raise RuntimeError(f"Can not find single AMI using filter: {filter_request['Filters']}")
        return amis[0]

    def provision_ubuntu_24_04_instance(self, name: str, security_groups=None, volume_size=None, key_name=None, instance_type="t3a.medium", asynchronous=True):
        """
        Provision instance.

        :param key_name: 
        :param name: 
        :param security_groups: 
        :param volume_size: 
        :return: 
        """

        if key_name is None:
            key = self.provision_ssh_key(f"key_{name}")
            key_name = key.name

        ec2_instance = EC2Instance({})

        ec2_instance.image_id = self.get_ubuntu24_04_image().id
        ec2_instance.instance_type = instance_type

        ec2_instance.key_name = key_name
        ec2_instance.region = self.environment_api.region
        ec2_instance.min_count = 1
        ec2_instance.max_count = 1

        ec2_instance.tags = self.environment_api.configuration.tags
        ec2_instance.tags.append({
            "Key": "Name",
            "Value": name
        })

        ec2_instance.ebs_optimized = True
        ec2_instance.instance_initiated_shutdown_behavior = "stop"

        ec2_instance.network_interfaces = [
            {
                "AssociatePublicIpAddress": False,
                "DeleteOnTermination": True,
                "Description": "Primary network interface",
                "DeviceIndex": 0,
                "Groups": [
                    security_group.id for security_group in security_groups
                ],
                "Ipv6AddressCount": 0,
                "SubnetId": self.environment_api.private_subnets[0].id,
                "InterfaceType": "interface",
            }
        ]

        ec2_instance.block_device_mappings = [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeSize": volume_size or 30,
                    "VolumeType": "gp3",
                },
            }
        ]
        ec2_instance.monitoring = {"Enabled": False}
        self.environment_api.aws_api.provision_ec2_instance(ec2_instance, wait_until_active=asynchronous)
        return ec2_instance

    def stop_instance(self, name=None):
        """
        Stop EC2 instance.

        :param name:
        :return:
        """

        if not name:
            raise NotImplementedError("Name was not set")
        ec2_instance = self.get_instance(name=name, update_info=True)
        if not ec2_instance:
            raise ValueError(f"Was not able to find instance by {name=}")
        self.environment_api.aws_api.ec2_client.stop_instance(ec2_instance)

    def provision_internal_alb_security_group(self):
        """
        Provision internal ALB security group.

        :return:
        """

        return self.provision_security_group(f"sg_{self.environment_api.configuration.environment_level}-{self.environment_api.configuration.environment_name}-internal-alb",
                                      "Internal ALB security group")

    def security_group_add_rule(self, destination_group: EC2SecurityGroup, source_group: Union[EC2SecurityGroup, str]=None, port_range=None):
        """
        Add rule to security group.
        :param destination_group:
        :param source_group:
        :param port_range:
        :return:
        """

        if not self.environment_api.aws_api.ec2_client.update_security_group_information(destination_group):
            raise RuntimeError("Failed to update security group information")

        if not port_range:
            raise NotImplementedError("port_range was not set")

        if not source_group:
            raise NotImplementedError("source_group was not set")

        source_group_id = None
        if isinstance(source_group, EC2SecurityGroup):
            source_group_id = source_group.id

        if isinstance(source_group, str):
            source_group_id = source_group


        desired_permission = {
            "IpProtocol": "tcp",
            "FromPort": port_range[0],
            "ToPort": port_range[1],
            "UserIdGroupPairs": [
                {
                    "GroupId": source_group_id,
                }
            ],
        }

        for permission in destination_group.ip_permissions:
            if permission.get("FromPort") == port_range[0] and \
                permission.get("ToPort") == port_range[1] and \
                permission.get("UserIdGroupPairs")[0].get("GroupId") == source_group_id:
                return True
        destination_group.ip_permissions.append(desired_permission)
        return self.environment_api.aws_api.ec2_client.provision_security_group(destination_group)

    def provision_ssh_key(self, name):
        """
        Standard.

        :return:
        """

        key_pair = KeyPair({})
        key_pair.name = name
        key_pair.key_type = "ed25519"
        key_pair.region = self.environment_api.region
        key_pair.tags = self.environment_api.get_tags_with_name(key_pair.name)

        self.environment_api.aws_api.provision_key_pair(key_pair, save_to_secrets_manager=True,
                                        secrets_manager_region=self.environment_api.region
                                            )

        return key_pair