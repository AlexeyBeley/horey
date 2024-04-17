"""
AWS Lambda representation
"""
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class InternetGateway(AwsObject):
    """
    AWS AvailabilityZone class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "InternetGatewayId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Attachments": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "Tags": self.init_default_attr,
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
        """
        Standard
        :param dict_src:
        :return:
        """
        init_options = {
            "InternetGatewayId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Attachments": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard
        :return:
        """
        request = {"TagSpecifications": [
            {"ResourceType": "internet-gateway", "Tags": self.tags}
        ]}

        return request
