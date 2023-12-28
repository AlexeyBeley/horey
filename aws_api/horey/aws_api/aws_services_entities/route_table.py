"""
AWS Lambda representation
"""
import copy

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class RouteTable(AwsObject):
    """
    AWS AvailabilityZone class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.associations = []
        self.routes = []
        self.vpc_id = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {
            "RouteTableId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Associations": self.init_default_attr,
            "PropagatingVgws": self.init_default_attr,
            "Routes": self.init_default_attr,
            "Tags": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "OwnerId": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"VpcId": self.vpc_id, "TagSpecifications": [
            {"ResourceType": "route-table", "Tags": self.tags}
        ]}

        return request

    def generate_associate_route_table_request(self, desired_route_table):
        """
        Standard.

        :return:
        """

        create_associations = []

        desired_subnets = []
        for association in desired_route_table.associations:
            if association.get("AssociationState") is not None:
                raise NotImplementedError(f"State not supported: {association}")
            desired_subnets.append(association["SubnetId"])

        self_subnets = []
        for association in self.associations:
            if association.get("AssociationState") != {"State": "associated"}:
                raise NotImplementedError(f"State not supported: {association}")
            self_subnets.append(association["SubnetId"])

        for self_subnet in self_subnets:
            if self_subnet in desired_subnets:
                continue

            raise NotImplementedError(f"Route disassociation is not yet implemented: {self_subnet}")

        for desired_subnet in desired_subnets:
            if desired_subnet in self_subnets:
                continue

            request = {"RouteTableId": self.id,
                       "SubnetId": desired_subnet
                       }
            create_associations.append(request)

        if len(create_associations) > 1:
            raise NotImplementedError(create_associations)

        return create_associations[0] if create_associations else None

    # pylint: disable = too-many-branches
    def generate_change_route_requests(self, desired_route_table, declarative=True):
        """
        Create or change route rules.

        :param desired_route_table:
        :param declarative: Desired state should be implemented as is. Not declarative: only add desired routes.
        :return: create_requests, replace_requests
        """

        create_requests, replace_requests = [], []
        desired_routes_by_destination = {route["DestinationCidrBlock"]: route for route in desired_route_table.routes}

        del_routes_errors = []
        for self_route in self.routes:
            if self_route.get("GatewayId") == "local":
                continue
            if self_route["State"] != "active":
                raise RuntimeError(f"Can not handle inactive route: {self.id}, {self_route}")
            if declarative and self_route["DestinationCidrBlock"] not in desired_routes_by_destination:
                del_routes_errors.append(self_route)

        if del_routes_errors:
            raise NotImplementedError(f"Erasing routes not implemented: {desired_route_table.region.region_mark}, {self.id}, {del_routes_errors}")

        for route in self.routes:
            if "DestinationCidrBlock" not in route:
                raise ValueError(f"Unsupported route: {self.id} {route}")

        self_routes_by_destination = {route["DestinationCidrBlock"]: route for route in self.routes}
        for desired_route in desired_route_table.routes:
            if desired_route.get("State") is not None:
                raise NotImplementedError(f"Can not handle setting state: {self.id}, {desired_route}")
            destination = desired_route["DestinationCidrBlock"]
            if destination not in self_routes_by_destination:
                request = copy.deepcopy(desired_route)
                request["RouteTableId"] = self.id
                create_requests.append(request)
            else:
                if desired_route.get("GatewayId") is None and \
                        self_routes_by_destination[destination].get("GatewayId") is None and \
                        desired_route.get("NatGatewayId") is None and \
                        self_routes_by_destination[destination].get("NatGatewayId"):
                    raise NotImplementedError(f"Other gateways not implemented: {self.id}, {desired_route}")
                if desired_route.get("GatewayId") != self_routes_by_destination[destination].get("GatewayId") or \
                    desired_route.get("NatGatewayId") != self_routes_by_destination[destination].get("NatGatewayId"):
                    if not declarative:
                        raise RuntimeError("Destructive changes should be declarative.")
                    request = copy.deepcopy(desired_route)
                    request["RouteTableId"] = self.id
                    replace_requests.append(request)

        return create_requests, replace_requests

    def check_subnet_associated(self, subnet_id):
        """
        Check if the subnet associated with the route.

        :param subnet_id:
        :return:
        """

        for association in self.associations:
            if "SubnetId" not in association:
                continue
            if association["SubnetId"] == subnet_id and \
                association["AssociationState"] == {"State": "associated"}:
                return True
        return False

    def get_default_route(self):
        """
        Return default route if exists.

        :return:
        """

        for route in self.routes:
            if route["State"] != "active":
                continue
            if route["DestinationCidrBlock"] == "0.0.0.0/0":
                return route
        return None
