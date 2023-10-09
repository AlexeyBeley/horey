"""
AWS SNS Topic representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class SNSTopic(AwsObject):
    """
    AWS SNSTopic class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.attributes = None
        self.arn = None
        self._name = None

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
            "TopicArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"Name": self.name, "Attributes": self.attributes, "Tags": self.tags}

        return request

    def generate_tag_resource_request(self, desired_sns_topic):
        """
        Standard.

        :param desired_sns_topic:
        :return:
        """

        if self.tags != desired_sns_topic.tags:
            return {"ResourceArn": self.arn, "Tags": self.tags}

        return None

    @property
    def name(self):
        if self._name is None:
            try:
                self._name = self.arn.split(":")[5]
            except AttributeError as error_instance:
                raise RuntimeError("Both name and arn are None") from error_instance

        return self._name

    @name.setter
    def name(self, value):
        self._name = value
