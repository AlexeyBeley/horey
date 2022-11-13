"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class DynamoDBTable(AwsObject):
    """
    AWS DynamoDBTable class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.arn = None
        self.provisioned_throughput = None
        self.tags = None
        self.billing_mode = None
        self.stream_specification = None
        self.sse_specification = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "TableArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "TableName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "TableId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "TableStatus": self.init_default_attr,
            "AttributeDefinitions": self.init_default_attr,
            "KeySchema": self.init_default_attr,
            "CreationDateTime": self.init_default_attr,
            "ProvisionedThroughput": self.init_default_attr,
            "TableSizeBytes": self.init_default_attr,
            "ItemCount": self.init_default_attr,
            "StreamSpecification": self.init_default_attr,
            "LatestStreamLabel": self.init_default_attr,
            "LatestStreamArn": self.init_default_attr,
            "SSEDescription": self.init_default_attr,
            "BillingModeSummary": self.init_default_attr,
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

    def update_from_raw_response(self, dict_src):
        init_options = {
            "TableArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "TableName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "TableId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "TableStatus": self.init_default_attr,
            "AttributeDefinitions": self.init_default_attr,
            "KeySchema": self.init_default_attr,
            "CreationDateTime": self.init_default_attr,
            "ProvisionedThroughput": self.init_default_attr,
            "TableSizeBytes": self.init_default_attr,
            "ItemCount": self.init_default_attr,
            "StreamSpecification": self.init_default_attr,
            "LatestStreamLabel": self.init_default_attr,
            "LatestStreamArn": self.init_default_attr,
            "SSEDescription": self.init_default_attr,
            "BillingModeSummary": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["TableName"] = self.name
        request["AttributeDefinitions"] = self.attribute_definitions
        request["KeySchema"] = self.key_schema

        if self.provisioned_throughput is not None:
            request["ProvisionedThroughput"] = self.provisioned_throughput

        if self.billing_mode is not None:
            request["BillingMode"] = self.billing_mode

        if self.stream_specification is not None:
            request["StreamSpecification"] = self.stream_specification

        request["Tags"] = self.tags if self.tags is not None else []
        for tag in request["Tags"]:
            if tag["Key"].lower() == "name":
                break
        else:
            request["Tags"].append({"Key": "Name", "Value": self.name})

        if self.sse_specification is not None:
            request["SSESpecification"] = self.sse_specification

        return request

    @property
    def region(self):
        if self._region is not None:
            return self._region

        raise NotImplementedError()
        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
