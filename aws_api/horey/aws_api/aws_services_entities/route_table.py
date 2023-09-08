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

    def generate_associate_route_table_request(self):
        """
        Standard.

        :return:
        """

        request = {"RouteTableId": self.id}
        if len(self.associations) > 1:
            raise NotImplementedError()
        request["SubnetId"] = self.associations[0]["SubnetId"]
        return request

    def generate_create_route_requests(self):
        """
        response = client.create_route(
        DestinationCidrBlock='string',
        DestinationIpv6CidrBlock='string',
        DestinationPrefixListId='string',
        DryRun=True|False,
        VpcEndpointId='string',
        EgressOnlyInternetGatewayId='string',
        GatewayId='string',
        InstanceId='string',
        NatGatewayId='string',
        TransitGatewayId='string',
        LocalGatewayId='string',
        CarrierGatewayId='string',
        NetworkInterfaceId='string',
        RouteTableId='string',
        VpcPeeringConnectionId='string'
        )
        """
        lst_ret = []
        for route in self.routes:
            request = copy.deepcopy(route)
            request["RouteTableId"] = self.id
            lst_ret.append(request)

        return lst_ret

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
