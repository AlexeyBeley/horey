"""
Class to represent ec2 instance
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.aws_services_entities.network_interface import NetworkInterface


class EC2Instance(AwsObject):
    """
    Class to represent ec2 instance
    """
    def __init__(self, dict_src, from_cache=False):
        """
        Init EC2 instance with boto3 dict
        :param dict_src:
        """
        super().__init__(dict_src)
        self.private_dns_name = None
        self.public_dns_name = None
        self.network_interfaces = []
        self.tags = {}

        if from_cache:
            self._init_instance_from_cache(dict_src)
            return

        init_options = {
                        "InstanceId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
                        "NetworkInterfaces": self.init_interfaces,
                        "Tags": self.init_tags,
                        "AmiLaunchIndex": self.init_default_attr,
                        "ImageId": self.init_default_attr,
                        "InstanceType": self.init_default_attr,
                        "KeyName": self.init_default_attr,
                        "LaunchTime": self.init_default_attr,
                        "Monitoring": self.init_default_attr,
                        "Placement": self.init_default_attr,
                        "PrivateDnsName": self.init_default_attr,
                        "PrivateIpAddress": self.init_default_attr,
                        "ProductCodes": self.init_default_attr,
                        "PublicDnsName": self.init_default_attr,
                        "State": self.init_default_attr,
                        "StateTransitionReason": self.init_default_attr,
                        "SubnetId": self.init_default_attr,
                        "VpcId": self.init_default_attr,
                        "Architecture": self.init_default_attr,
                        "BlockDeviceMappings": self.init_default_attr,
                        "ClientToken": self.init_default_attr,
                        "EbsOptimized": self.init_default_attr,
                        "EnaSupport": self.init_default_attr,
                        "Hypervisor": self.init_default_attr,
                        "IamInstanceProfile": self.init_default_attr,
                        "RootDeviceName": self.init_default_attr,
                        "RootDeviceType": self.init_default_attr,
                        "SecurityGroups": self.init_default_attr,
                        "SourceDestCheck": self.init_default_attr,
                        "StateReason": self.init_default_attr,
                        "VirtualizationType": self.init_default_attr,
                        "CpuOptions": self.init_default_attr,
                        "PublicIpAddress": self.init_default_attr,
                        "Association": self.init_default_attr,
                        "CapacityReservationSpecification": self.init_default_attr,
                        "KernelId": self.init_default_attr,
                        "Platform": self.init_default_attr,
                        "SpotInstanceRequestId": self.init_default_attr,
                        "InstanceLifecycle": self.init_default_attr,
                        "HibernationOptions": self.init_default_attr,
                        "MetadataOptions": self.init_default_attr,
                        "EnclaveOptions": self.init_default_attr,
                        "BootMode": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

        tag_name = self.get_tag("Name")
        self.name = tag_name if tag_name else self.id

    def _init_instance_from_cache(self, dict_src):
        """
        Init self from preserved dict.
        :param dict_src:
        :return:
        """
        options = {"network_interfaces": self._init_network_interfaces_from_cache}

        self._init_from_cache(dict_src, options)

    def _init_network_interfaces_from_cache(self, _, lst_src):
        """
        Nonstandard init of objects called from standard init_from_cache
        :param _:
        :param lst_src:
        :return:
        """
        if self.network_interfaces:
            raise NotImplementedError()

        for interface in lst_src:
            self.network_interfaces.append(NetworkInterface(interface, from_cache=True))

    def init_tags(self, _, tags):
        """
        Init tags
        :param _:
        :param tags:
        :return:
        """
        for tag in tags:
            self.tags[tag["Key"]] = tag["Value"]

    def get_tag(self, key):
        """
        Fetch tag value by name
        :param key:
        :return:
        """
        return self.tags.get(key)

    def init_interfaces(self, _, interfaces):
        """
        Init interface self objects
        :param _:
        :param interfaces:
        :return:
        """
        for interface in interfaces:
            self.network_interfaces.append(NetworkInterface(interface))

    def get_dns_records(self):
        """
        Get all self dns records.
        :return:
        """
        ret = []
        if self.private_dns_name:
            ret.append(self.private_dns_name)

        if self.public_dns_name:
            ret.append(self.public_dns_name)

        return ret

    def get_all_ips(self):
        """
        Get all self ips.
        :return:
        """
        return [end_point["ip"].copy() for end_point in self.get_security_groups_endpoints()]

    def get_security_groups_endpoints(self):
        """
        Return security group endpoints - what end points the security group protects.
        :return:
        """
        lst_ret = []
        for inter in self.network_interfaces:
            lst_ret_inter = inter.get_security_groups_endpoints()
            for ret_inter in lst_ret_inter:
                ret_inter["service_name"] = "EC2"
                ret_inter["device_name"] = self.name
                ret_inter["device_id"] = self.id
                lst_ret.append(ret_inter)

        return lst_ret

    def create(self):
        return {
            "DisableApiTermination": True,
            "InstanceInitiatedShutdownBehavior": 'stop',
            "NetworkInterfaces": [
                {
                    'AssociatePublicIpAddress': True,
                    'DeleteOnTermination': True,
                    'DeviceIndex': 0,
                    'Groups': [
                        SEC_GROUP,
                    ],
                    'Ipv6AddressCount': 0,
                    'SubnetId': SUBNET,
                    'InterfaceType': 'interface',
                    'NetworkCardIndex': 0
                },
            ],
            "CreditSpecification": {
                'CpuCredits': 'unlimited'
            },
            "BlockDeviceMappings": [
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 20,
                        'VolumeType': 'standard',
                    },
                },
                {
                    'DeviceName': '/dev/sdb',
                    'Ebs': {
                        'DeleteOnTermination': False,
                        'VolumeSize': 40,
                        'VolumeType': 'standard',
                    },
                },
                {
                    'DeviceName': '/dev/sdc',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 20,
                        'VolumeType': 'standard',
                    },
                },
            ],
            "ImageId": AMI_ID,
            "InstanceType": 't2.micro',
            "KeyName": 'jenkins-key',
            "Monitoring": {
                'Enabled': True
            },
            "TagSpecifications": [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'jenkins-master-tmp'
                        },
                        {
                            'Key': 'env_level',
                            'Value': 'production'
                        },
                        {
                            'Key': 'env_name',
                            'Value': 'production'
                        },

                    ]
                },
            ],
            "IamInstanceProfile": {
                'Name': 'service-role-jenkins'
            },
            "MaxCount": 1,
            "MinCount": 1
        }
