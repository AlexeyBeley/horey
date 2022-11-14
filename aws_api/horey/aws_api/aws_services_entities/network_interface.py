"""
Class to represent ec2 instance
"""
import pdb

from horey.network.ip import IP
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class NetworkInterface(AwsObject):
    """
    Class representing ec2 network interface
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.groups = []
        self.private_ip_addresses = []
        self.subnet_id = None
        self.description = None
        self.ipv6_addresses = []
        self.private_ip_address = None
        self.attachment = None
        self.association = None

        if from_cache:
            self._init_interface_from_cache(dict_src)
            return

        init_options = {
            "NetworkInterfaceId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
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
            "AvailabilityZone": self.init_default_attr,
            "RequesterId": self.init_default_attr,
            "RequesterManaged": self.init_default_attr,
            "TagSet": self.init_default_attr,
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
            "private_ip_address": self._init_private_ip_address_from_cache,
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

        self.private_ip_address = IP(value + "/32")

    def get_private_addresses(self):
        all_addresses = []
        for dict_addr in self.private_ip_addresses:
            all_addresses.append(dict_addr["PrivateIpAddress"])
        return all_addresses

    def get_public_addresses(self):
        if self.association is None:
            raise RuntimeError(
                f"self.association is None in  interface {self.dict_src}"
            )
        return [IP(self.association["PublicIp"] + "/32")]

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
                description = (
                    "Inteface: SubnetId: {} NetworkInterfaceId: {}- '{}'".format(
                        self.subnet_id, self.id, self.description
                    )
                )
                dict_ret = {
                    "sg_id": sec_grp["GroupId"],
                    "sg_name": sec_grp["GroupName"],
                    "description": description,
                }
                if "Association" in dict_addr:
                    all_addresses.append(dict_addr["Association"]["PublicIp"])
                    dict_ret["ip"] = IP(
                        dict_addr["Association"]["PublicIp"], int_mask=32
                    )
                    dict_ret["dns"] = dict_addr["Association"]["PublicDnsName"]
                    lst_ret.append(dict_ret)

                # Private
                dict_ret = {
                    "sg_id": sec_grp["GroupId"],
                    "sg_name": sec_grp["GroupName"],
                    "description": description,
                }
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

    def get_used_security_group_ids(self):
        return [group["GroupId"] for group in self.groups]
