"""
CloudfrontFunction

"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.common_utils.common_utils import CommonUtils


class CloudfrontFunction(AwsObject):
    """
    AWS identity representation class
    """

    def __init__(self, dict_src, from_cache=False):
        dict_src = self.normalize_raw_data(dict_src)

        super().__init__(dict_src)
        self.name = None
        self.function_config = None
        self.stage = None
        self.created_time = None
        self.last_modified_time = None
        self.location = None
        self.function_code = None
        self.e_tag = None

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

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        required_attrs = ["Name", "FunctionConfig", "FunctionCode"]

        request = {}
        for attr_name in required_attrs:
            attr_value = getattr(self, CommonUtils.camel_case_to_snake_case(attr_name))
            if not attr_value:
                raise RuntimeError(f"Attribute value was not set: {attr_name}")
            request[attr_name] = attr_value

        return request

    def generate_publish_request(self):
        """
        Standard.

        :return:
        """

        required_attrs = ["Name", "ETag"]

        request = {}
        for attr_name in required_attrs:
            attr_value = getattr(self, CommonUtils.camel_case_to_snake_case(attr_name))
            if not attr_value:
                raise RuntimeError(f"Attribute value was not set: {attr_name}")
            request[attr_name] = attr_value

        request["IfMatch"] = request.pop("ETag")

        return request

    def generate_update_request(self, desired_function):
        """
        Standard.

        :return:
        """
        if self.name != desired_function.name:
            raise ValueError(f"Cloudfront functions' names do not match: {desired_function.name=}, {self.name=}")

        required_attrs = ["Name", "ETag", "FunctionCode", "FunctionConfig"]

        request = {}
        changed = False
        for attr_name in required_attrs:
            self_value = getattr(self, CommonUtils.camel_case_to_snake_case(attr_name))
            desired_value = getattr(desired_function, CommonUtils.camel_case_to_snake_case(attr_name))
            if not self_value:
                raise RuntimeError(
                    f"Attribute value was not set in self, this means the self is not initialized correctly: {attr_name}")

            if not desired_value:
                request[attr_name] = self_value
                continue

            if desired_value != self_value:
                changed = True

            request[attr_name] = desired_value

        request["IfMatch"] = request.pop("ETag")

        return request if changed else None

    def generate_test_request(self, event_object):
        """

        :param event_object:
        :return:
        """
        required_attrs = ["Name", "ETag"]

        request = {}
        for attr_name in required_attrs:
            attr_value = getattr(self, CommonUtils.camel_case_to_snake_case(attr_name))
            if not attr_value:
                raise RuntimeError(f"Attribute value was not set: {attr_name}")
            request[attr_name] = attr_value
        request["IfMatch"] = request.pop("ETag")

        if self.stage:
            request["Stage"] = self.stage

        request["EventObject"] = event_object

        return request

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """
        required_attrs = ["Name", "ETag"]

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
            "Name": self.init_default_attr,
            "FunctionConfig": self.init_default_attr,
            "Stage": self.init_default_attr,
            "CreatedTime": self.init_default_attr,
            "LastModifiedTime": self.init_default_attr,
            "FunctionCode": self.init_default_attr,
            "Location": self.init_default_attr,
            "ETag": self.init_default_attr,
            "Status": self.init_default_attr,
            "ContentType": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @staticmethod
    def normalize_raw_data(dict_src):
        """
        Cleaning the AWS garbage.

        :param dict_src:
        :return:
        """

        for nested_key_name in ["FunctionSummary", "FunctionMetadata"]:
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
