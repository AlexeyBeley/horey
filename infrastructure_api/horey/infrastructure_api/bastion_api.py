"""
Standard bastion maintainer.

"""
import os

from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.aws_api.base_entities.region import Region
from horey.deployer.whatismyip import fetch_ip_from_google


class BastionAPI:
    """
    Manage bastion.

    """

    def __init__(self, environment: EnvironmentAPI, name):
        self.environment = environment
        self.name = name
        self.role_name = f"role_instance_{name}"
        self.profile_name = f"instance_profile_{name}"
        self.ssh_key_pair_name = f"key_pair_{name}"
        self.security_group_name = f"sg_{name}"

    def provision(self):
        """
        Create/update bastion server.

        :return:
        """

        profile = self.provision_instance_profile()
        self.provision_ssh_key_pair()
        self.provision_security_group()
        instance = self.provision_instance(profile)
        self.provision_bastion_services()
        self.provision_ssh_config()
        return instance

    def provision_instance_profile(self):
        """
        Provision bastion IAM role and instance profile.

        :return:
        """

        return self.environment.provision_instance_profile(self.role_name, self.profile_name)

    def provision_ssh_key_pair(self):
        """
        Provision Bastion SSH Key-pair.

        :return:
        """

        return self.environment.provision_ssh_key(self.ssh_key_pair_name)

    def provision_security_group(self):
        """
        Bastion SG

        :return:
        """
        address = fetch_ip_from_google()

        ip_permissions = [
            {"FromPort": 22,
             "ToPort": 22,
             "IpProtocol": "tcp",
             "IpRanges": [
                 {
                     "CidrIp": f"{address}/32",
                     "Description": "[self] to [bastion]:22"
                 }]
             }]

        return self.environment.provision_security_group(self.security_group_name, ip_permissions=ip_permissions)

    def provision_instance(self, iam_instance_profile):
        """
        Provision environment's bastion ec2 instance.

        :return:
        """

        security_group = self.environment.aws_api.get_security_group_by_vpc_and_name(self.environment.vpc,
                                                                                     self.security_group_name)

        ami = self.environment.get_ubuntu22_image()

        target = EC2Instance({})
        target.image_id = ami.id
        target.instance_type = "t3a.medium"

        target.key_name = self.ssh_key_pair_name
        target.region = self.environment.region
        target.min_count = 1
        target.max_count = 1

        target.tags = self.environment.configuration.tags
        target.tags.append({
            "Key": "Name",
            "Value": self.name
        })

        target.ebs_optimized = True
        target.instance_initiated_shutdown_behavior = "stop"

        target.network_interfaces = [
            {
                "AssociatePublicIpAddress": True,
                "DeleteOnTermination": True,
                "Description": "Primary network interface",
                "DeviceIndex": 0,
                "Groups": [
                    security_group.id
                ],
                "Ipv6AddressCount": 0,
                "SubnetId": self.environment.public_subnets[0].id,
                "InterfaceType": "interface",
            }
        ]

        target.block_device_mappings = [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeSize": 10,
                    "VolumeType": "gp3"
                },
            }
        ]
        target.monitoring = {"Enabled": True}

        target.iam_instance_profile = {"Arn": iam_instance_profile.arn}

        self.environment.aws_api.provision_ec2_instance(target)
        return target

    def provision_bastion_services(self):
        """
        Provision Bastion services - docker, ntp etc.

        :return:
        """

        return True

    def provision_ssh_config(self):
        """
        Generate configuration files.

        :return:
        """

        key_file_name = f"{self.ssh_key_pair_name}.key"
        self.environment.aws_api.get_secret_file(key_file_name,
                                                 str(self.environment.configuration.data_directory_path),
                                                 region=Region.get_region(
                                                     self.environment.configuration.secrets_manager_region))
        ec2_instance = self.environment.aws_api.get_alive_ec2_instance_by_name(self.environment.region, self.name)

        # "    ProxyJump bastion.development"

        str_ret = f"Host {self.name}\n" \
                  "    StrictHostKeyChecking no\n" \
                  "    IdentitiesOnly yes\n" \
                  "    UseKeychain yes\n" \
                  "    AddKeysToAgent yes\n" \
                  f"    Hostname {ec2_instance.public_ip_address}\n" \
                  "    User ubuntu\n" \
                  f"    IdentityFile {str(self.environment.configuration.data_directory_path / key_file_name)}\n" \
                  f"# ssh -F {self.environment.configuration.data_directory_path / self.name} {self.name}\n"

        config_file_path = self.environment.configuration.data_directory_path / self.name
        key_file_path = self.environment.configuration.data_directory_path / key_file_name
        with open(config_file_path, "w",
                  encoding="utf-8") as file_handler:
            file_handler.write(str_ret)
        os.chmod(key_file_path, 0o600)

        return True

    def dispose(self):
        """
        Create/update bastion server.

        :return:
        """
