"""
AWS SESV2EmailIdentity representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class SESV2EmailIdentity(AwsObject):
    """
    AWS SESV2EmailIdentity class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.arn = None
        self.tags = None
        self.identity_type = None
        self.verified_for_sending_status = None

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
        dict received from server.

        :param dict_src:
        :return:
        """

        init_options = {
            "IdentityName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "IdentityType": self.init_default_attr,
            "FeedbackForwardingStatus": self.init_default_attr,
            "VerifiedForSendingStatus": self.init_default_attr,
            "DkimAttributes": self.init_default_attr,
            "MailFromAttributes": self.init_default_attr,
            "Policies": self.init_default_attr,
            "Tags": self.init_default_attr,
            "SendingEnabled": self.init_default_attr,
            "VerificationStatus": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"EmailIdentity": self.name}

        return request

    @property
    def region(self):
        """
        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region


        :return:
        """

        if self._region is not None:
            return self._region

        raise NotImplementedError("region is None")

    @region.setter
    def region(self, value):
        """
        Region setter.

        :param value:
        :return:
        """

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
