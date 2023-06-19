"""
EKSCluster representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class EKSCluster(AwsObject):
    """
    AWS EKSCluster class
    """

    CLIENT_NAME = "eks"

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.arn = None
        self.endpoint = None
        self.certificate_authority = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "name": self.init_default_attr
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
            "name": self.init_default_attr,
            "arn": self.init_default_attr,
            "createdAt": self.init_default_attr,
            "version": self.init_default_attr,
            "endpoint": self.init_default_attr,
            "roleArn": self.init_default_attr,
            "resourcesVpcConfig": self.init_default_attr,
            "kubernetesNetworkConfig": self.init_default_attr,
            "logging": self.init_default_attr,
            "identity": self.init_default_attr,
            "status": self.init_default_attr,
            "certificateAuthority": self.init_default_attr,
            "platformVersion": self.init_default_attr,
            "tags": self.init_default_attr
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
