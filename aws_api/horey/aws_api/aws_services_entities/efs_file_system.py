"""
AWS Lambda representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EFSFileSystem(AwsObject):
    """
    AWS VPC class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.availability_zone_id = None
        self.throughput_mode = None
        self.provisioned_throughput_in_mibps = None
        self.file_system_protection = None

        if from_cache:
            self._init_from_cache(dict_src, {})
            return

        self.request_key_to_attribute_mapping = {"FileSystemId": "id"}
        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {"ThroughputMode": self.init_default_attr,
                        "FileSystemId": lambda x, y: self.init_default_attr(
                            x, y, formatted_name="id"
                        ),
                        "ProvisionedThroughputInMibps": self.init_default_attr,
                        "OwnerId": self.init_default_attr,
                        "CreationToken": self.init_default_attr,
                        "FileSystemArn": lambda x, y: self.init_default_attr(
                            x, y, formatted_name="arn"
                        ),
                        "CreationTime": self.init_default_attr,
                        "LifeCycleState": self.init_default_attr,
                        "Name": self.init_default_attr,
                        "NumberOfMountTargets": self.init_default_attr,
                        "SizeInBytes": self.init_default_attr,
                        "PerformanceMode": self.init_default_attr,
                        "Encrypted": self.init_default_attr,
                        "KmsKeyId": self.init_default_attr,
                        "AvailabilityZoneName": self.init_default_attr,
                        "AvailabilityZoneId": self.init_default_attr,
                        "Tags": self.init_default_attr,
                        "FileSystemProtection": self.init_default_attr,
                        }

        return self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.
        CreationToken='string',
    PerformanceMode='generalPurpose'|'maxIO',
    Encrypted=True|False,
    KmsKeyId='string',
    ThroughputMode='bursting'|'provisioned'|'elastic',
    ProvisionedThroughputInMibps=123.0,
    AvailabilityZoneName='string',
    Backup=True|False,
    Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
    ]

        :return:
        """

        return self.generate_request(["FileSystemId"],
                                     optional=["ThroughputMode", "ProvisionedThroughputInMibps"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """
        return self.generate_request(["FileSystemId"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

    def generate_update_request(self, desired_state):
        """
        Standard.

        :return:
        """

        required = ["FileSystemId"]
        self_request = self.generate_request(required,
                              optional=["ThroughputMode", "ProvisionedThroughputInMibps"],
                              request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)
        desired_state_request = desired_state.generate_request(required,
                              optional=["ThroughputMode", "ProvisionedThroughputInMibps"],
                              request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)

        request = {}
        for key in required:
            if self_request[key] != desired_state_request[key]:
                raise ValueError(f"Required key must be same: {key}")
            request[key] = desired_state_request[key]

        for key, desired_value in desired_state_request.items():
            if self_request.get(key) != desired_value:
                request[key] = desired_state_request[key]

        return None if len(request) == len(required) else request

    def get_tagname(self, ignore_missing_tag=False):
        """
        Name tag.

        :return:
        """

        if ignore_missing_tag:
            raise ValueError(f"Should not set {ignore_missing_tag=}")

        return self.get_tag("Name", casesensitive=True)
