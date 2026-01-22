"""
Standard EC2 maintainer.

"""

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

    def provision_security_group(self):
        """
        Provision log group.

        :param name:
        :return:
        """

        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.environment_api.vpc.id
        security_group.name = self.configuration.name
        security_group.description = security_group.name
        security_group.region = self.environment_api.region
        security_group.tags = self.environment_api.configuration.tags
        security_group.tags.append({
            "Key": "Name",
            "Value": security_group.name
        })

        if self.configuration.ip_permissions is not None:
            security_group.ip_permissions = self.configuration.ip_permissions

        self.environment_api.aws_api.provision_security_group(security_group, provision_rules=bool(self.configuration.ip_permissions))

        return security_group

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

    def provision_ubuntu_24_04_instance(self, name: str, security_groups=None, volume_size=None, key_name=None, instance_type="t3a.medium"):
        """
        Provision instance.

        :param key_name: 
        :param name: 
        :param security_groups: 
        :param volume_size: 
        :return: 
        """

        if key_name is None:
            raise NotImplementedError("key_name")

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
                "AssociatePublicIpAddress": True,
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
        ec2_instance.monitoring = {"Enabled": True}

        self.environment_api.aws_api.provision_ec2_instance(ec2_instance)
        return ec2_instance
