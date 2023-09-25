"""
CloudfrontFunction

"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils


class CloudfrontResponseHeadersPolicy(AwsObject):
    """
    AWS identity representation class
    """

    def __init__(self, dict_src, from_cache=False):

        dict_src = self.normalize_raw_data(dict_src)
        super().__init__(dict_src)
        self.e_tag = None
        self._name = None
        self.response_headers_policy_config = {}

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

    @property
    def name(self):
        if self._name is None:
            self._name = self.response_headers_policy_config["Name"]

        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        required_attrs = ["ResponseHeadersPolicyConfig"]

        request = {}
        for attr_name in required_attrs:
            attr_value = getattr(self, CommonUtils.camel_case_to_snake_case(attr_name))
            if not attr_value:
                raise RuntimeError(f"Attribute value was not set: {attr_name}")
            request[attr_name] = attr_value

        try:
            if not request["ResponseHeadersPolicyConfig"]["SecurityHeadersConfig"]["FrameOptions"]:
                del request["ResponseHeadersPolicyConfig"]["SecurityHeadersConfig"]["FrameOptions"]
        except KeyError:
            pass

        return request

    def generate_update_request(self, desired):
        """
        Standard.
        {'ResponseHeadersPolicyConfig':
        {'Comment': 'Response headers policy',
        'Name': 'sample',
        'SecurityHeadersConfig':
        {'XSSProtection':
        {'Override': True, 'Protection': True, 'ModeBlock': True},
        'FrameOptions': {}


        :return:
        """
        if self.name != desired.name:
            raise ValueError(f"Cloudfront cloudfront_response_headers_policy' names do not match: {desired.name=}, {self.name=}")

        required_attrs = ["Id", "ResponseHeadersPolicyConfig", "ETag"]

        request = {}
        changed = False
        for attr_name in required_attrs:
            self_value = getattr(self, CommonUtils.camel_case_to_snake_case(attr_name))
            desired_value = getattr(desired, CommonUtils.camel_case_to_snake_case(attr_name))
            if not self_value:
                raise RuntimeError(f"Attribute value was not set in self, this means the self is not initialized correctly: {attr_name}")

            if not desired_value:
                request[attr_name] = self_value
                continue

            if desired_value != self_value:
                changed = True

            request[attr_name] = desired_value

        try:
            if not request["ResponseHeadersPolicyConfig"]["SecurityHeadersConfig"]["FrameOptions"]:
                del request["ResponseHeadersPolicyConfig"]["SecurityHeadersConfig"]["FrameOptions"]
        except KeyError:
            pass

        request["IfMatch"] = request.pop("ETag")

        return request if changed else None

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """

        required_attrs = ["ETag", "Id"]

        request = {}
        for attr_name in required_attrs:
            attr_value = getattr(self, CommonUtils.camel_case_to_snake_case(attr_name))
            if not attr_value:
                raise RuntimeError(f"Attribute value was not set: {attr_name}")
            request[attr_name] = attr_value
        request["IfMatch"] = request.pop("ETag")
        return request

    def update_from_raw_response(self, dict_src):
        """
        Standard.
        from horey.common_utils.common_utils import CommonUtils
        for key in init_options: print(f"self.{CommonUtils.camel_case_to_snake_case(key)} = None")

        :param dict_src:
        :return:
        """

        dict_src = self.normalize_raw_data(dict_src)

        init_options = {
                        "FunctionARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
                        "ETag": self.init_default_attr,
                        "Type": self.init_default_attr,
                        "Id": self.init_default_attr,
                        "LastModifiedTime": self.init_default_attr,
                        "ResponseHeadersPolicyConfig": self.init_default_attr,

        }

        self.init_attrs(dict_src, init_options)

    @staticmethod
    def normalize_raw_data(dict_src):
        """
        Cleaning the AWS garbage.

        :param dict_src:
        :return:
        """

        for nested_key_name in ["ResponseHeadersPolicy"]:
            try:
                tmp_dict = dict_src.pop(nested_key_name)
                dict_src.update(tmp_dict)
            except KeyError:
                pass

        try:
            del dict_src["ResponseMetadata"]
        except KeyError:
            pass

        return dict_src
