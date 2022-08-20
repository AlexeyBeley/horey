"""
AWS ec2 security group representation
"""
import pdb

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

    def generate_modify_ip_permissions_requests(self, target_security_group):
        """
        Generate add_request and revoke_request

        @param target_security_group:
        @return:
        """

        add_request, revoke_request = [], []

        for self_permission in self.ip_permissions:
            if not any([self.check_permissions_equal(self_permission, target_permission)
                        for target_permission in target_security_group.ip_permissions]):
                revoke_request.append(self_permission)

        for target_permission in target_security_group.ip_permissions:
            if not any([self.check_permissions_equal(target_permission, self_permission)
                        for self_permission in self.ip_permissions]):
                add_request.append(target_permission)

        add_request = {"GroupId": self.id, "IpPermissions": add_request} if add_request else None
        revoke_request = {"GroupId": self.id, "IpPermissions": revoke_request} if revoke_request else None

        return add_request, revoke_request

    @staticmethod
    def check_permissions_equal(permission_1, permission_2):
        """
        Check weather two permissions are equal.

        @param permission_1:
        @param permission_2:
        @return:
        """

        for key, value in permission_1.items():
            target_value = permission_2.get(key)
            if (value or target_value is not None) and target_value != value:
                return False
        return True

    def generate_modify_ip_permissions_egress_requests(self, target_security_group):
        """
        Generate add_request and revoke_request

        @param target_security_group:
        @return:
        """

        raise NotImplementedError(f"generate_modify_ip_permissions_egress_requests: {target_security_group.name}")

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

    def update_from_raw_response(self, dict_src):
        """
        Update from server dict response.

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
