"""
Standard EC2 maintainer.

"""

from horey.h_logger import get_logger
from horey.aws_api.aws_clients.ec2_client import EC2SecurityGroup, EC2Instance, KeyPair
from horey.infrastructure_api.ec2_api_configuration_policy import EC2APIConfigurationPolicy
from horey.infrastructure_api.access_manager_api import AccessManagerAPI, AccessManagerAPIConfigurationPolicy
logger = get_logger()


class EC2API:
    """
    Manage ECS.

    """

    def __init__(self, configuration: EC2APIConfigurationPolicy, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api
        self._access_manager_api = None

    def provision_security_group(self, name, description=None, ip_permissions=None):
        """
        Provision log group.

        :param description:
        :param ip_permissions:
        :param name:
        :return:
        """

        security_group = EC2SecurityGroup({})
        security_group.vpc_id = self.environment_api.vpc.id
        security_group.name = name
        security_group.description = description or name
        security_group.region = self.environment_api.region
        security_group.tags = self.environment_api.configuration.tags
        security_group.tags.append({
            "Key": "Name",
            "Value": security_group.name
        })

        security_group.ip_permissions = ip_permissions

        self.environment_api.aws_api.provision_security_group(security_group, provision_rules=bool(ip_permissions))

        return security_group

    def provision_ec2_instance(self, name, security_group, profile, public=False, subnet=None):
        """
        Provision instance.

        :param public:
        :param subnet:
        :param name:
        :param security_group:
        :param profile:
        :return:
        """

        ami = self.get_ubuntu_image("24.04")

        ec2_instance = EC2Instance({})
        ec2_instance.image_id = ami.id
        ec2_instance.instance_type = self.get_instance_type(cpu=2)

        key = self.provision_ssh_key(f"key_{name}")
        ec2_instance.key_name = key.name
        ec2_instance.region = self.environment_api.region
        ec2_instance.min_count = 1
        ec2_instance.max_count = 1

        ec2_instance.tags = self.environment_api.configuration.tags
        ec2_instance.tags.append({
            "Key": "Name",
            "Value": name
        })

        ec2_instance.ebs_optimized = True
        ec2_instance.instance_initiated_shutdown_behavior = "terminate"

        if subnet is None:
            if public:
                subnet_id = self.environment_api.get_all_public_subnets()[0].id
            else:
                subnet_id = self.environment_api.get_all_private_subnets()[0].id
        else:
            subnet_id = subnet.id
            route_table = self.environment_api.aws_api.find_route_table_by_subnet(subnet)
            if not route_table:
                raise ValueError(f"Was not able to find subnet's route table: {subnet_id}")

            gateway_type = "GatewayId" if public else "NatGatewayId"

            for route in route_table.routes:
                if route.get("DestinationCidrBlock") == "0.0.0.0/0" and route.get(gateway_type) is not None:
                    break
            else:
                raise RuntimeError(f"Subnet {subnet_id=} type deterimned by route table is not matching"
                                   f" the explicitly set type {public=}")

        ec2_instance.network_interfaces = [
            {
                "AssociatePublicIpAddress": public,
                "DeleteOnTermination": True,
                "Description": f"{name} Primary network interface",
                "DeviceIndex": 0,
                "Groups": [
                    security_group.id
                ],
                "Ipv6AddressCount": 0,
                "SubnetId": subnet_id,
                "InterfaceType": "interface",
            }
        ]

        ec2_instance.block_device_mappings = [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeSize": 30,
                    "VolumeType": "gp3"
                },
            }
        ]

        ec2_instance.monitoring = {"Enabled": False}

        ec2_instance.iam_instance_profile = {"Arn": profile.arn}

        self.environment_api.aws_api.ec2_client.provision_ec2_instance(ec2_instance, wait_until_active=True)
        return ec2_instance

    def get_ubuntu_image(self, ubuntu_version):
        """
        Get latest Ubuntu22 image in this region.

        :return:
        """

        param = self.environment_api.aws_api.ssm_client.get_region_parameter(self.environment_api.region,
                                                             f"/aws/service/canonical/ubuntu/server/{ubuntu_version}/stable/current/amd64/hvm/ebs-gp3/ami-id")

        filter_request = {"ImageIds": [param.value]}
        amis = self.environment_api.aws_api.ec2_client.get_region_amis(self.environment_api.region, custom_filters=filter_request)
        if len(amis) != 1:
            raise RuntimeError(f"Can not find single AMI using filter: {filter_request['Filters']}")

        return amis[0]

    def get_instance_type(self, cpu=1):
        """
        Select instance type.

        :param cpu:
        :return:
        """

        return "t3.medium"

    def provision_ssh_key(self, name, secrets_manager_region=None):
        """
        Standard.

        :return:
        """

        key_pair = KeyPair({})
        key_pair.name = name
        key_pair.key_type = "ed25519"
        key_pair.region = self.environment_api.region
        key_pair.tags = self.environment_api.configuration.tags
        key_pair.tags.append({
            "Key": "Name",
            "Value": name
        })

        self.environment_api.aws_api.provision_key_pair(key_pair, save_to_secrets_manager=True,
                                        secrets_manager_region=secrets_manager_region or self.environment_api.region)

        return key_pair

    @property
    def access_manager_api(self):
        """
        Standard.

        :return:
        """

        if self._access_manager_api is None:
            config = AccessManagerAPIConfigurationPolicy()
            self._access_manager_api = AccessManagerAPI(config, self.environment_api)
        return self._access_manager_api

    def provision_bastion(self):
        """
        Bastion

        :return:
        """

        role_name = f"role_{self.environment_api.configuration.environment_level}_bastion_u24"
        role = self.access_manager_api.provision_role(role_name, assume_role_policy=self.access_manager_api.get_service_assume_role_policy("ec2"))

        instance_profile_name = f"inst_profile_{self.environment_api.configuration.environment_level}_bastion_u24"
        profile = self.access_manager_api.provision_instance_profile(instance_profile_name, role)

        sec_group = self.provision_security_group(f"sg_bastion_u24_{self.environment_api.configuration.environment_level}")

        machine_name = f"bastion.{self.environment_api.configuration.environment_level}.u24"
        return self.provision_ec2_instance(machine_name, sec_group, profile, public=True)
