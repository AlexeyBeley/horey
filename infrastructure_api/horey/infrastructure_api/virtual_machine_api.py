"""
Standard bastion maintainer.

"""

from horey.infrastructure_api.environment_api import EnvironmentAPI
from horey.aws_api.aws_services_entities.ec2_instance import EC2Instance
from horey.infrastructure_api.virtual_machine_api_configuration_policy import VirtualMachineAPIConfigurationPolicy


class VirtualMachineAPI:
    """
    Manage bastion.

    """

    def __init__(self, configuration:VirtualMachineAPIConfigurationPolicy, environment_api: EnvironmentAPI):
        self.configuration = configuration
        self.environment_api = environment_api

        self.configuration.project_name = self.environment_api.configuration.project_name
        self.configuration.project_name_abbr = self.environment_api.configuration.project_name_abbr
        self.configuration.environment_name = self.environment_api.configuration.environment_name
        self.configuration.environment_level = self.environment_api.configuration.environment_level

    def provision(self):
        """
        Create/update bastion server.

        :return:
        """

        self.provision_instance_profile()
        self.provision_ssh_key_pair()
        self.provision_security_group()
        instance = self.provision_instance()
        self.provision_system_functions()
        return instance

    def provision_instance_profile(self):
        """
        Provision bastion IAM role and instance profile.

        :return:
        """

        return self.environment_api.provision_instance_profile(self.configuration.role_name, self.configuration.profile_name)

    def provision_ssh_key_pair(self):
        """
        Provision Bastion SSH Key-pair.

        :return:
        """

        return self.environment_api.provision_ssh_key(self.configuration.ssh_key_pair_name)

    def provision_security_group(self):
        """
        Bastion SG

        :return:
        """

        return self.environment_api.provision_security_group(self.configuration.security_group_name)

    def provision_instance(self):
        """
        Provision environment's bastion ec2 instance.

        :return:
        """

        security_group = self.environment_api.get_security_groups([self.configuration.security_group_name], single=True)
        iam_instance_profile = self.environment_api.get_instance_profile(self.configuration.profile_name)

        ami = self.get_ubuntu24_image()

        ec2_instance = EC2Instance({})
        ec2_instance.image_id = ami.id
        ec2_instance.instance_type = self.configuration.instance_type

        ec2_instance.key_name = self.configuration.ssh_key_pair_name
        ec2_instance.region = self.environment_api.region

        ec2_instance.tags = self.environment_api.configuration.tags
        ec2_instance.tags.append({
            "Key": "Name",
            "Value": f"{self.configuration.name}_{self.configuration.environment_name}_v24"
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
                    security_group.id
                ],
                "Ipv6AddressCount": 0,
                "SubnetId": self.environment_api.private_subnets[0].id if self.configuration.private else self.environment_api.public_subnets[0].id,
                "InterfaceType": "interface",
            }
        ]

        ec2_instance.block_device_mappings = [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeSize": self.configuration.volume_size,
                    "VolumeType": "gp3"
                },
            }
        ]
        ec2_instance.monitoring = {"Enabled": True}

        ec2_instance.iam_instance_profile = {"Arn": iam_instance_profile.arn}
        ec2_instance.min_count = 1
        ec2_instance.max_count = 1

        self.environment_api.aws_api.provision_ec2_instance(ec2_instance)
        return ec2_instance

    def provision_system_functions(self):
        """
        Provision Bastion services - docker, ntp etc.

        :return:
        """

        return True

    def dispose(self):
        """
        Create/update bastion server.

        :return:
        """

    def get_ubuntu24_image(self):
        """
        Get latest Ubuntu22 image in this region.
        filters_req = {"ParameterFilters": [{
            'Key': 'Name',
            'Option': 'BeginsWith',
            'Values': [
                '/aws/service/canonical/ubuntu/server',
            ]
        }]}
        all_params = self.environment_api.aws_api.ssm_client.describe_parameters_raw(region=self.environment_api.region, filters_req=filters_req)

        :return:
        """

        param = self.environment_api.aws_api.ssm_client.get_region_parameter(self.environment_api.region,
                                                             "/aws/service/canonical/ubuntu/server/24.10/stable/current/arm64/hvm/ebs-gp3/ami-id")

        filter_request = {"ImageIds": [param.value]}
        amis = self.environment_api.aws_api.ec2_client.get_region_amis(self.environment_api.region, custom_filters=filter_request)
        if len(amis) != 1:
            raise RuntimeError(f"Can not find single AMI using filter: {filter_request['Filters']}")

        return amis[0]
