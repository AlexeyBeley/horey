"""
AWS ec2 security group representation
"""

from horey.network.service import ServiceTCP, ServiceUDP, ServiceICMP, ServiceRDP
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EC2SecurityGroup(AwsObject):
    """
    AWS ec2 security group representation
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.dns_name = None
        self.ip_permissions = []
        self.ip_permissions_egress = []
        self.vpc_id = None
        self.description = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
                        "GroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
                        "Description": self.init_default_attr,
                        "IpPermissions": self.init_default_attr,
                        "OwnerId": self.init_default_attr,
                        "GroupId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
                        "IpPermissionsEgress": self.init_default_attr,
                        "Tags": self.init_default_attr,
                        "VpcId": self.init_default_attr,
                        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init self from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def get_dns_records(self):
        """
        Get my dns record as list.
        :return:
        """
        return [self.dns_name] if self.dns_name else []

    def get_ingress_pairs(self):
        """
        Ip, service pairs

        @return:
        """

        lst_ret = []
        for ip_permission in self.ip_permissions:
            if ip_permission.ip_protocol == "-1":
                service = ServiceTCP.any()
            elif ip_permission.ip_protocol == "tcp":
                service = ServiceTCP()
                service.start = ip_permission.from_port
                service.end = ip_permission.to_port
            elif ip_permission.ip_protocol == "udp":
                service = ServiceUDP()
                service.start = ip_permission.from_port
                service.end = ip_permission.to_port
            elif ip_permission.ip_protocol == "27":
                service = ServiceRDP()
            elif ip_permission.ip_protocol == "icmp":
                service = ServiceICMP.any()
            else:
                raise NotImplementedError(ip_permission.ip_protocol)

            for address in ip_permission.ipv4_ranges:
                lst_ret.append((address.ip, service))

        return lst_ret

    def generate_create_request(self):
        """
        Self explanatory.

        @return:
        """

        request = {"GroupName": self.name, "Description": self.description}
        if self.vpc_id is not None:
            request["VpcId"] = self.vpc_id
        if self.tags is not None:
            request["TagSpecifications"] = [{
                                        "ResourceType": "security-group",
                                        "Tags": self.tags}]

        return request

    def update_from_raw_create(self, dict_src):
        """
        Self explanatory.

        @param dict_src:
        @return:
        """

        init_options = {
            "GroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Description": self.init_default_attr,
            "IpPermissions": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "GroupId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "IpPermissionsEgress": self.init_default_attr,
            "Tags": self.init_default_attr,
            "VpcId": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)
