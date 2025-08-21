"""
AWS object representation.
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class S3AccessPoint(AwsObject):
    """
    AWS VPC class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.name = None
        self.bucket_account_id = None

        if from_cache:
            self._init_from_cache(dict_src, {})
            return

        self.request_key_to_attribute_mapping = {}
        self.update_from_raw_response(dict_src)

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """

        init_options = {"Name": self.init_default_attr,
                        "NetworkOrigin": self.init_default_attr,
                        "VpcConfiguration": self.init_default_attr,
                        "Bucket": self.init_default_attr,
                        "AccessPointArn": self.init_default_attr,
                        "Alias": self.init_default_attr,
                        "BucketAccountId": self.init_default_attr,
                        "PublicAccessBlockConfiguration": self.init_default_attr,
                        "CreationDate": self.init_default_attr,
                        "Endpoints": self.init_default_attr,
                        }

        return self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        raise NotImplementedError("""
        if not self.get_tagname():
            raise RuntimeError("Tag Name was not set")

        return self.generate_request(["Name", "Scope", "IPAddressVersion", "Addresses", "Tags"],
                                     optional=["Description"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)
        """)

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """
        raise NotImplementedError("""
        return self.generate_request(["LockToken", "Id", "Scope", "Name"],
                                     request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)
        """)

    def generate_update_request(self, desired_state):
        """
        Standard.

        :return:
        """
        raise NotImplementedError("""
        required = ["LockToken", "Id", "Scope", "Name"]
        self_request = self.generate_request(required,
                                             optional=["Description", "Addresses"],
                                             request_key_to_attribute_mapping=self.request_key_to_attribute_mapping)
        desired_state_request = desired_state.generate_request(required,
                                                               optional=["Description", "Addresses"],
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
        """)
