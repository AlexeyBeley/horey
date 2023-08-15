"""
AWS ec2 security group representation
"""
import copy

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
            "GroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
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
        add_request, revoke_request, update_description = [], [], []

        for self_permission in self.split_permissions(self.ip_permissions):
            if not any(
                (
                    self.check_permissions_equal(
                        self_permission,
                        target_permission,
                        check_without_description=True,
                    )
                    for target_permission in self.split_permissions(
                        target_security_group.ip_permissions
                    )
                )
            ):
                revoke_request.append(self_permission)
        if len(revoke_request) == len(self.ip_permissions):
            raise ValueError(f"Can not automatically delete all rules in security group {target_security_group.id=}. "
                             f"You can do it only manually!")


        for target_permission in self.split_permissions(
            target_security_group.ip_permissions
        ):
            # No equals (Do not check description differences)
            if not any(
                (
                    self.check_permissions_equal(target_permission, self_permission)
                    for self_permission in self.split_permissions(self.ip_permissions)
                )
            ):
                # Check weather there are equal by location but differ by description.
                if any(
                    (
                        self.check_permissions_equal(
                            target_permission,
                            self_permission,
                            check_without_description=True,
                        )
                        for self_permission in self.split_permissions(
                            self.ip_permissions
                        )
                    )
                ):
                    update_description.append(target_permission)
                else:
                    add_request.append(target_permission)

        add_request = (
            {"GroupId": self.id, "IpPermissions": add_request} if add_request else None
        )
        revoke_request = (
            {"GroupId": self.id, "IpPermissions": revoke_request}
            if revoke_request
            else None
        )
        update_description = (
            {"GroupId": self.id, "IpPermissions": update_description}
            if update_description
            else None
        )

        return add_request, revoke_request, update_description

    @staticmethod
    def split_permissions(permissions):
        """
        Split permission to granular permissions.
        Why? Because AWS!!! That's why!
        It summarizes the permissions by proto and port and you can't just live a simple life,
        you need this piece of garbage code to make it work!

        @param permissions:
        @return:
        """

        lst_ret = []
        for permission in permissions:
            base_permission = {"IpProtocol": permission["IpProtocol"]}

            try:
                base_permission["FromPort"] = permission["FromPort"]
            except KeyError:
                pass

            try:
                base_permission["ToPort"] = permission["ToPort"]
            except KeyError:
                pass

            try:
                for ip_range in permission["IpRanges"]:
                    new_permission = copy.deepcopy(base_permission)
                    new_permission["IpRanges"] = [ip_range]
                    lst_ret.append(new_permission)
            except KeyError:
                pass

            try:
                for ipv6_range in permission["Ipv6Ranges"]:
                    new_permission = copy.deepcopy(base_permission)
                    new_permission["Ipv6Ranges"] = [ipv6_range]
                    lst_ret.append(new_permission)
            except KeyError:
                pass

            try:
                for user_id_group_pair in permission["UserIdGroupPairs"]:
                    new_permission = copy.deepcopy(base_permission)
                    new_permission["UserIdGroupPairs"] = [user_id_group_pair]
                    lst_ret.append(new_permission)
            except KeyError:
                pass

            try:
                for prefix_list_id in permission["PrefixListIds"]:
                    new_permission = copy.deepcopy(base_permission)
                    new_permission["PrefixListIds"] = [prefix_list_id]
                    lst_ret.append(new_permission)
            except KeyError:
                pass

        return lst_ret

    @staticmethod
    def check_permissions_equal(
        permission_1, permission_2, check_without_description=False
    ):
        """
        Check weather two permissions are equal.

        @param permission_1:
        @param permission_2:
        @param check_without_description:
        @return:
        """
        keys_without_description = ["FromPort", "IpProtocol", "ToPort"]

        for key, value in permission_1.items():
            target_value = permission_2.get(key)

            # target value was not set
            if target_value is None:
                # value was not set
                if not value:
                    continue

                return False

            if target_value == value:
                continue

            # raw comparison (compare value with description) OR a key is scalar
            if not check_without_description or key in keys_without_description:
                return False

            if not isinstance(target_value, list) or not isinstance(value, list):
                raise ValueError(
                    f"For key: {key}, {value}, {target_value} in {permission_1}, {permission_2}"
                )

            # must be split already
            if len(target_value) != 1 or len(value) != 1:
                raise ValueError(f"{value}, {target_value}")

            value_location = {
                _key: _value
                for _key, _value in value[0].items()
                if _key != "Description"
            }
            target_value_location = {
                _key: _value
                for _key, _value in target_value[0].items()
                if _key != "Description"
            }
            if value_location != target_value_location:
                return False

        return True

    def generate_modify_ip_permissions_egress_requests(self, target_security_group):
        """
        Generate add_request and revoke_request

        @param target_security_group:
        @return:
        """

        raise NotImplementedError(
            f"generate_modify_ip_permissions_egress_requests: {target_security_group.name}"
        )

    def generate_create_request(self):
        """
        Self explanatory.

        @return:
        """

        request = {"GroupName": self.name, "Description": self.description}
        if self.vpc_id is not None:
            request["VpcId"] = self.vpc_id
        if self.tags is not None:
            request["TagSpecifications"] = [
                {"ResourceType": "security-group", "Tags": self.tags}
            ]

        return request

    def update_from_raw_create(self, dict_src):
        """
        Self explanatory.

        @param dict_src:
        @return:
        """

        init_options = {
            "GroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
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
            "GroupName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "Description": self.init_default_attr,
            "IpPermissions": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "GroupId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "IpPermissionsEgress": self.init_default_attr,
            "Tags": self.init_default_attr,
            "VpcId": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)
