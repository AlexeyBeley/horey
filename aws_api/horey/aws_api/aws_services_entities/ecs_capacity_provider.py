"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ECSCapacityProvider(AwsObject):
    """
    AWS AutoScalingGroup class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "capacityProviderArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "status": self.init_default_attr,
            "name": self.init_default_attr,
            "tags": self.init_default_attr,
            "autoScalingGroupProvider": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_value_from_raw_response(self, raw_value):
        raise NotImplementedError()
        pdb.set_trace()

    def generate_create_request(self):
        """
        response = client.create_capacity_provider(
       name='string',
       autoScalingGroupProvider={
        'autoScalingGroupArn': 'string',
        'managedScaling': {
            'status': 'ENABLED'|'DISABLED',
            'targetCapacity': 123,
            'minimumScalingStepSize': 123,
            'maximumScalingStepSize': 123,
            'instanceWarmupPeriod': 123
        },
        'managedTerminationProtection': 'ENABLED'|'DISABLED'
    },
    tags=[
        {
            'key': 'string',
            'value': 'string'
        },
    ]
)
        """
        request = dict()
        request["name"] = self.name
        request["autoScalingGroupProvider"] = self.auto_scaling_group_provider
        request["tags"] = self.tags

        return request

    def update_from_raw_create(self, dict_src):
        raise NotImplementedError()
        pdb.set_trace()
        init_options = {
            "ECSClusterId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "ECSClusterArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "AvailabilityZone": self.init_default_attr,
            "AvailabilityZoneId": self.init_default_attr,
            "AvailableIpAddressCount": self.init_default_attr,
            "CidrBlock": self.init_default_attr,
            "DefaultForAz": self.init_default_attr,
            "MapPublicIpOnLaunch": self.init_default_attr,
            "MapCustomerOwnedIpOnLaunch": self.init_default_attr,
            "State": self.init_default_attr,
            "VpcId": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "AssignIpv6AddressOnCreation": self.init_default_attr,
            "Ipv6CidrBlockAssociationSet": self.init_default_attr,
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def region(self):
        raise NotImplementedError()
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        raise NotImplementedError()
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
