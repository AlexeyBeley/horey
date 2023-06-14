"""
EKSAddon representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class EKSAddon(AwsObject):
    """
    AWS EKSAddon class
    """

    CLIENT_NAME = "eks"

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.cluster_name = None
        self.arn = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "addonName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "clusterName": self.init_default_attr,
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
        Update the object from server response.
,
        :param dict_src:
        :return:
        """
        init_options = {
            "addonName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "addonArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "clusterName": self.init_default_attr,
            "status": self.init_default_attr,
            "addonVersion": self.init_default_attr,
            "health": self.init_default_attr,
            'createdAt': self.init_default_attr,
            'modifiedAt': self.init_default_attr,
            'serviceAccountRoleArn': self.init_default_attr,
            'tags': self.init_default_attr,
            'publisher': self.init_default_attr,
            'owner': self.init_default_attr,
            'marketplaceInformation': self.init_default_attr,
            'configurationValues': self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Generate request to create the resource.

        :return:
        """
        # pylint: disable=not-an-iterable
        request = {"name": self.name}

        return request

    @property
    def region(self):
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
