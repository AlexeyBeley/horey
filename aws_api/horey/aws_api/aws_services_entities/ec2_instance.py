"""
Class to represent ec2 instance
"""
import pdb

import sys
import os
sys.path.insert(0, os.path.join(os.path.abspath("../.."), "IP", "ip", "src"))
from ip import IP
from aws_object import AwsObject


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
        options = {'launch_time': self.init_date_attr_from_cache_string,
                   'network_interfaces': self._init_network_interfaces_from_cache}

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
            self.network_interfaces.append(self.NetworkInterface(interface, from_cache=True))

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
            self.network_interfaces.append(self.NetworkInterface(interface))

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

    class NetworkInterface(AwsObject):
        """
        Class representing ec2 network interface
        """
        def __init__(self, dict_src, from_cache=False):
            super(EC2Instance.NetworkInterface, self).__init__(dict_src)
            self.groups = []
            self.private_ip_addresses = []
            self.subnet_id = None
            self.description = None
            self.ipv6_addresses = []
            self.private_ip_address = None

            if from_cache:
                self._init_interface_from_cache(dict_src)
                return

            init_options = {
                            "NetworkInterfaceId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
                            "PrivateIpAddress": self._init_private_ip_address,
                            "Attachment": self.init_default_attr,
                            "Description": self.init_default_attr,
                            "Groups": self.init_default_attr,
                            "Ipv6Addresses": self.init_default_attr,
                            "MacAddress": self.init_default_attr,
                            "OwnerId": self.init_default_attr,
                            "PrivateDnsName": self.init_default_attr,
                            "PrivateIpAddresses": self.init_default_attr,
                            "SourceDestCheck": self.init_default_attr,
                            "Status": self.init_default_attr,
                            "Association": self.init_default_attr,
                            "SubnetId": self.init_default_attr,
                            "VpcId": self.init_default_attr,
                            "InterfaceType": self.init_default_attr,
                            }

            self.init_attrs(dict_src, init_options)
            self.name = self.id

        def _init_interface_from_cache(self, dict_src):
            """
            Init self from conserved dict
            :param dict_src:
            :return:
            """
            options = {
                        'private_ip_address': self._init_private_ip_address_from_cache,
                       }

            self._init_from_cache(dict_src, options)

        def convert_to_dict(self):
            """
            Convert the object to a cache dict
            :return:
            """
            custom_types = {IP: lambda x: x.convert_to_dict()}
            return self.convert_to_dict_static(self.__dict__, custom_types=custom_types)

        def _init_private_ip_address_from_cache(self, _, value):
            """
            Init object from cache dict
            :param _:
            :param value:
            :return:
            """
            if self.private_ip_address is not None:
                raise NotImplementedError()
            self.private_ip_address = IP(value, from_dict=True)

        def _init_private_ip_address(self, _, value):
            """
            Init private address from dict.
            :param _:
            :param value:
            :return:
            """

            self.private_ip_address = IP(value+"/32")

        def get_security_groups_endpoints(self):
            """
            Get all endpoints reached by security groups.
            :return:
            """

            lst_ret = []

            all_addresses = []
            for sec_grp in self.groups:
                for dict_addr in self.private_ip_addresses:
                    # Public
                    description = "Inteface: SubnetId: {} NetworkInterfaceId: {}- '{}'".format(
                        self.subnet_id, self.id, self.description)
                    dict_ret = {"sg_id": sec_grp["GroupId"], "sg_name": sec_grp["GroupName"], "description": description}
                    if "Association" in dict_addr:
                        all_addresses.append(dict_addr["Association"]["PublicIp"])
                        dict_ret["ip"] = IP(dict_addr["Association"]["PublicIp"], int_mask=32)
                        dict_ret["dns"] = dict_addr["Association"]["PublicDnsName"]
                        lst_ret.append(dict_ret)

                    # Private
                    dict_ret = {"sg_id": sec_grp["GroupId"], "sg_name": sec_grp["GroupName"], "description": description}
                    all_addresses.append(dict_addr["PrivateIpAddress"])
                    dict_ret["ip"] = IP(dict_addr["PrivateIpAddress"], int_mask=32)
                    if "PrivateDnsName" in dict_addr:
                        dict_ret["dns"] = dict_addr["PrivateDnsName"]

                    lst_ret.append(dict_ret)

                if self.private_ip_address.str_address not in all_addresses:
                    raise Exception

                if self.dict_src["Ipv6Addresses"]:
                    pdb.set_trace()

                for dict_addr in self.ipv6_addresses:
                    pdb.set_trace()
                    all_addresses.append(dict_addr["Association"]["PublicIp"])
                    all_addresses.append(dict_addr["PrivateIpAddress"])
                if self.private_ip_address.str_address not in all_addresses:
                    raise Exception
            return lst_ret
