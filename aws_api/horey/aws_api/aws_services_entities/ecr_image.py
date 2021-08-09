"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ECRImage(AwsObject):
    """
    AWS VPC class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        
        init_options = {
            "registryId": self.init_default_attr,
            "repositoryName": self.init_default_attr,
            "imageDigest": self.init_default_attr,
            "imageTags": self.init_default_attr,
            "imageSizeInBytes": self.init_default_attr,
            "imagePushedAt": self.init_default_attr,
            "imageScanStatus": self.init_default_attr,
            "imageScanFindingsSummary": self.init_default_attr,
            "imageManifestMediaType": self.init_default_attr,
            "artifactMediaType": self.init_default_attr,
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
        raise NotImplementedError()
        """
        TagSpecifications=[
        {
            'ResourceType': 'client-vpn-endpoint'|'customer-gateway'|'dedicated-host'|'dhcp-options'|'egress-only-internet-gateway'|'elastic-ip'|'elastic-gpu'|'export-image-task'|'export-instance-task'|'fleet'|'fpga-image'|'host-reservation'|'image'|'import-image-task'|'import-snapshot-task'|'instance'|'internet-gateway'|'key-pair'|'launch-template'|'local-gateway-route-table-vpc-association'|'natgateway'|'network-acl'|'network-interface'|'network-insights-analysis'|'network-insights-path'|'placement-group'|'reserved-instances'|'route-table'|'security-group'|'snapshot'|'spot-fleet-request'|'spot-instances-request'|'subnet'|'traffic-mirror-filter'|'traffic-mirror-session'|'traffic-mirror-target'|'transit-gateway'|'transit-gateway-attachment'|'transit-gateway-connect-peer'|'transit-gateway-multicast-domain'|'transit-gateway-route-table'|'volume'|'vpc'|'vpc-peering-connection'|'vpn-connection'|'vpn-gateway'|'vpc-flow-log',
            'Tags': [
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ]
        },
    ],
       """
        request = dict()
        request["CidrBlock"] = self.cidr_block
        request["AvailabilityZoneId"] = self.availability_zone_id
        request["VpcId"] = self.vpc_id
        request["TagSpecifications"] = [{
                                        "ResourceType": "subnet",
                                        "Tags": self.tags}]

        return request

    def update_from_raw_create(self, dict_src):
        raise NotImplementedError()
        pdb.set_trace()
        init_options = {
            "ECRImageId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "ECRImageArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
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
