"""
EKSFargateProfile representation

"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class EKSAccessEntry(AwsObject):
    """
    AWS EKSFargateProfile class
    """

    CLIENT_NAME = "eks"

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.cluster_name = None
        self.principal_arn = None
        self.kubernetes_groups = None
        self.client_request_token = None
        self.username = None
        self.type = None

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
        Update the object from server response.

        :param dict_src:
        :return:
        """

        init_options = {
            "accessEntryArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "clusterName": self.init_default_attr,
            "kubernetesGroups": self.init_default_attr,
            "createdAt": self.init_default_attr,
            "principalArn": self.init_default_attr,
            "modifiedAt": self.init_default_attr,
            "tags": self.init_default_attr,
            "username": self.init_default_attr,
            "type": self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options)

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


    def generate_create_request(self):
        """
        Generate raw dict request.

        @return:
        """

        if not self.tags:
            raise RuntimeError("Tags required when creating access entry")

        request = {"clusterName": self.cluster_name,
                   "tags": self.tags,
                   "principalArn": self.principal_arn}

        self.extend_request_with_optional_parameters(request, ["kubernetesGroups",
                                                               "clientRequestToken",
                                                               "username",
                                                               "type"])

        return request

    def generate_modify_request(self, desired_state):
        """
        Standard.

        :param desired_state:
        :return:
        """

        return self.generate_request_aws_object_modify(desired_state, ["clusterName", "principalArn", "tags"],
                                                       optional=["kubernetesGroups",
                                                                 "clientRequestToken",
                                                                 "username",
                                                                 "type",
                                                                 ],
                                                           )
