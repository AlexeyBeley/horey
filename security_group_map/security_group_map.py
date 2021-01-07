"""
Module handling security group map - nodes and edges.
"""
from enum import Enum
from service import Service
from dns import DNS
from h_flow import HFlow
from aws_api import AWSAPI


class SecurityGroupMapEdge:
    """
    Class representing Edge.
    """
    # pylint: disable=R0913
    def __init__(self, edge_type, value, ip_protocol, from_port, to_port, description):
        self.type = edge_type
        self.dst = value
        self.ip_protocol = ip_protocol
        self.from_port = from_port
        self.to_port = to_port
        self.description = description
        self._service = None

    def __str__(self):
        return "SecurityGroupMapEdge: {} {} {} {} {} {} {}".format(
            self.type, self.dst, self.ip_protocol, self.from_port, self.to_port, self.description, self._service)

    @property
    def service(self):
        """
        Edge service.
        :return:
        """
        if self._service is None:
            if self.ip_protocol is None:
                self._service = Service.any()
            else:
                raise NotImplementedError("Replacement of pdb.set_trace")

        return self._service

    @service.setter
    def service(self, value):
        """
        Should not be set explicit.
        :param value:
        :return:
        """
        raise NotImplementedError("Not settable")

    class Type(Enum):
        """
            Possible Security group values
        """

        SECURITY_GROUP = 0
        IP = 1


class SecurityGroupMapNode:
    """
    Class representing a node
    """
    def __init__(self, security_group):
        self.security_group = security_group
        self.outgoing_edges = []
        self.incoming_edges = []
        self.data = []
        self._h_flow_filters_dst = None
        self._h_flow_filters_src = None

        for permission in self.security_group.ip_permissions:
            self.add_edges_from_permission(self.incoming_edges, permission)

        for permission in self.security_group.ip_permissions_egress:
            self.add_edges_from_permission(self.outgoing_edges, permission)

    @property
    def h_flow_filters_dst(self):
        """
        Get dst filters
        """
        if not self._h_flow_filters_dst:
            lst_filters = []

            for data_unit in self.data:
                for edge in self.outgoing_edges:
                    if edge.type is SecurityGroupMapEdge.Type.IP:

                        h_filter = HFlow.Tunnel.Traffic()

                        h_filter.info = [data_unit, edge]

                        h_filter.dns_src = DNS(data_unit["dns"])
                        if "ip" not in data_unit:
                            ip = AWSAPI.find_ips_from_dns(h_filter.dns_src)[0]
                        else:
                            ip = data_unit["ip"]

                        h_filter.ip_src = ip

                        h_filter.ip_dst = edge.dst
                        h_filter.service_dst = edge.service

                        lst_filters.append(h_filter)
                    else:
                        raise NotImplementedError("Replacement of pdb.set_trace")

            self._h_flow_filters_dst = lst_filters

        return self._h_flow_filters_dst

    @h_flow_filters_dst.setter
    def h_flow_filters_dst(self, value):
        """
        Get dst filters
        :param value:
        :return:
        """
        raise NotImplementedError("Not yet implemented")

    @property
    def h_flow_filters_src(self):
        """
        Return filters src
        :return:
        """
        raise NotImplementedError("Replacement of pdb.set_trace")

    @h_flow_filters_src.setter
    def h_flow_filters_src(self, value):
        """
        Set the src filters
        :param value:
        :return:
        """
        raise NotImplementedError("Replacement of pdb.set_trace")

    @staticmethod
    def add_edges_from_permission(dst_lst, permission):
        """
        Don't know what to write here :(
        :param dst_lst:
        :param permission: Security Group Permissions
        :return:
        """
        lst_ret = []
        edge_type = SecurityGroupMapEdge.Type.SECURITY_GROUP
        for dict_pair in permission.user_id_group_pairs:
            description = dict_pair["GroupName"] if "GroupName" in dict_pair else None
            description = dict_pair["Description"] if "Description" in dict_pair else description
            for key in dict_pair:
                if key not in ["Description", "GroupId", "UserId", "GroupName"]:
                    raise Exception(key)
            lst_ret.append((edge_type, dict_pair["GroupId"], description))

        edge_type = SecurityGroupMapEdge.Type.IP
        for addr in permission.ipv4_ranges:
            lst_ret.append((edge_type, addr.ip, addr.description))

        for addr in permission.ipv6_ranges:
            lst_ret.append((edge_type, addr.ip, addr.description))

        for edge_type, value, description in lst_ret:
            ip_protocol = permission.ip_protocol if hasattr(permission, "ip_protocol") else None
            from_port = permission.from_port if hasattr(permission, "from_port") else None
            to_port = permission.to_port if hasattr(permission, "to_port") else None
            edge = SecurityGroupMapEdge(edge_type, value, ip_protocol, from_port, to_port, description)
            dst_lst.append(edge)

        if permission.prefix_list_ids:
            raise Exception

    def add_data(self, data):
        """
        Add data
        :param data:
        :return:
        """
        self.data.append(data)


class SecurityGroupsMap:
    """
    Class representing the map
    """
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        """
        Add single node.
        :param node:
        :return:
        """
        if node.security_group.id in self.nodes:
            raise Exception

        self.nodes[node.security_group.id] = node

    def add_node_data(self, security_group_id, data):
        """
        Add single node data.
        :param security_group_id:
        :param data:
        :return:
        """
        try:
            self.nodes[security_group_id].add_data(data)
        except Exception:
            print("todo: remove ' def add_node_data'")

    def find_outgoing_paths(self, sg_id, seen_grps=None):
        """
        Legacy stuff. Don't know what to write here.
        :param sg_id:
        :param seen_grps:
        :return:
        """
        raise NotImplementedError("Replacement of pdb.set_trace")

    def apply_dst_h_flow_filters_multihop(self, h_flow):
        """
        Apply filters
        :param h_flow:
        :return:
        """
        return self.recursive_apply_dst_h_flow_filters_multihop(h_flow, [], [])

    def recursive_apply_dst_h_flow_filters_multihop(self, h_flow, lst_path, lst_seen):
        """
        Apply filters
        :param h_flow:
        :param lst_path:
        :param lst_seen:
        :return:
        """
        node = self.nodes[h_flow.end_point_src.custom["security_group_id"]]

        if node.security_group.id in lst_seen:
            raise NotImplementedError("Replacement of pdb.set_trace")
        lst_seen.append(node.security_group.id)
        lst_path.append(node.security_group.id)
        for edge in node.outgoing_edges:
            if edge.type == SecurityGroupMapEdge.Type.IP:
                h_flow.apply_dst_filters_on_start(node.h_flow_filters_dst)

                lst_path.append(edge.dst)
                return lst_path
            if edge.type == SecurityGroupMapEdge.Type.SECURITY_GROUP:
                return self.recursive_apply_dst_h_flow_filters_multihop(self.nodes[edge.dst], lst_path, [])
            raise NotImplementedError("Replacement of pdb.set_trace")
