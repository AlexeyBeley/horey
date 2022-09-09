"""
Class to represent ec2 instance
"""
import copy
import datetime
import pdb

from enum import Enum
from horey.aws_api.base_entities.region import Region
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
        self.iam_instance_profile = None
        self.max_count = None
        self.min_count = None
        self.security_groups = None
        self.subnet_id = None

        if from_cache:
            self._init_instance_from_cache(dict_src)
            return

        init_options = {
            "InstanceId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "NetworkInterfaces": self.init_interfaces,
            "Tags": self.init_default_attr,
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
            "PlatformDetails": self.init_default_attr,
            "UsageOperation": self.init_default_attr,
            "UsageOperationUpdateTime": self.init_default_attr,
            "PrivateDnsNameOptions": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

        tag_name = self.get_tagname("Name")
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

    @property
    def region(self):
        if self._region is None:
            az_split = self.placement["AvailabilityZone"].split("-")
            if len(az_split) != 3:
                raise ValueError(self.placement["AvailabilityZone"])

            az_index = ""
            for _char in az_split[2]:
                if not _char.isdigit():
                    break
                az_index += _char
            self._region = Region.get_region(f"{az_split[0]}-{az_split[1]}-{az_index}")
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    def init_interfaces(self, _, interfaces):
        """
        Init interface self objects
        :param _:
        :param interfaces:
        :return:
        """
        self.network_interfaces = []
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

    def get_private_addresses(self):
        lst_ret = []
        for inter in self.network_interfaces:
            lst_ret += inter.get_private_addresses()
        return lst_ret

    def get_public_addresses(self):
        lst_ret = []
        for inter in self.network_interfaces:
            lst_ret += inter.get_public_addresses()
        return lst_ret

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

    def update_from_raw_response(self, dict_src):
        init_options = {
            "InstanceId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "NetworkInterfaces": self.init_interfaces,
            "Tags": self.init_default_attr,
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
            "PlatformDetails": self.init_default_attr,
            "UsageOperation": self.init_default_attr,
            "UsageOperationUpdateTime": self.init_default_attr,
            "PrivateDnsNameOptions": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_snapshots_request(self):
        request = dict()
        request["TagSpecifications"] = [{
            "ResourceType": "snapshot",
            "Tags": self.tags}]
        request["InstanceSpecification"] = {"InstanceId": self.id, "ExcludeBootVolume": False}
        request["Description"] = self.get_tagname()
        request["CopyTagsFromSource"] = 'volume'

        return request

    def generate_dispose_request(self):
        request = dict()
        request["InstanceIds"] = [self.id]
        return request

    def generate_create_image_request(self, snapshots_raw=None):
        request = dict()
        request["Description"] = self.get_tagname()
        request["Name"] = self.get_tagname()+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        request["InstanceId"] = self.id
        request["NoReboot"] = False
        request["TagSpecifications"] = [{
            "ResourceType": "image",
            "Tags": self.tags}]

        #############
        if snapshots_raw is not None:
            blocks_request = []
            for self_block in self.block_device_mappings:
                for snapshot in snapshots_raw:
                    if self_block["Ebs"]["VolumeId"] == snapshot["VolumeId"]:
                        block_request = {"DeviceName": self_block["DeviceName"],
                                      "Ebs": {
                                          "DeleteOnTermination": self_block["Ebs"]["DeleteOnTermination"],
                                          "SnapshotId": snapshot["SnapshotId"],
                                          "VolumeSize": snapshot["VolumeSize"],
                                          "VolumeType": "gp2"
                                      }}
                        if snapshot["VolumeSize"] == 30:
                            block_request['VirtualName'] = "/dev/xvda"
                        else:
                            block_request['VirtualName'] = "/dev/sda1"

                        blocks_request.append(block_request)
                        break
                else:
                    raise RuntimeError(f"Can not find snapshot of {self_block}")

            #request["BlockDeviceMappings"] = blocks_request

        return request

    def generate_create_request(self):
        request = dict()
        request["InstanceInitiatedShutdownBehavior"] = self.instance_initiated_shutdown_behavior
        request["NetworkInterfaces"] = self.network_interfaces
        # request["CreditSpecification"] = {
        #        'CpuCredits': 'unlimited'
        #    }
        request["BlockDeviceMappings"] = self.block_device_mappings

        request["ImageId"] = self.image_id

        request["InstanceType"] = self.instance_type

        # request["EbsOptimized"] = self.ebs_optimized

        request["KeyName"] = self.key_name
        request["Monitoring"] = self.monitoring

        request["MaxCount"] = self.max_count
        request["MinCount"] = self.min_count

        if self.iam_instance_profile is not None:
            request["IamInstanceProfile"] = self.iam_instance_profile

        tags = copy.deepcopy(self.tags)
        for tag in tags:
            if tag["Key"].lower() == "name":
                tag["Key"] = "Name"
                break
        else:
            raise RuntimeError(f"Tag 'Name' must present when provisioning ec2 instance. {request}")

        request["TagSpecifications"] = [{
            "ResourceType": "instance",
            "Tags": tags}]

        return request

    def get_status(self):
        return self.get_state()

    def get_state(self):
        if self.state["Name"] == "pending":
            return self.State.PENDING
        elif self.state["Name"] == "running":
            return self.State.RUNNING
        elif self.state["Name"] == "shutting-down":
            return self.State.SHUTTING_DOWN
        elif self.state["Name"] == "terminated":
            return self.State.TERMINATED
        elif self.state["Name"] == "stopping":
            return self.State.STOPPING
        elif self.state["Name"] == "stopped":
            return self.State.STOPPED
        else:
            raise NotImplementedError(self.state["Name"])

    class State(Enum):
        PENDING = 0
        RUNNING = 1
        SHUTTING_DOWN = 2
        TERMINATED = 3
        STOPPING = 4
        STOPPED = 5
