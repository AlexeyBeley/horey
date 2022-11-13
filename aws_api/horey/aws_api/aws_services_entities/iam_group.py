"""
Module handling IAM group object
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class IamGroup(AwsObject):
    """Class representing AWS IAM Group"""

    def __init__(self, dict_src, from_cache=False):
        """
        Init Iam user with boto3 dict

        :param dict_src:
        """
        self.policies = None
        self.attached_policies = None

        super().__init__(dict_src)

        if from_cache:
            self._init_group_from_cache(dict_src)
            return

        init_options = {
            "GroupId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "GroupName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Arn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "Path": self.init_default_attr,
            "CreateDate": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_group_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {}

        self._init_from_cache(dict_src, options)

    def update_extended(self, dict_src):
        """
        Update self attributes from extended API Reply.
        :param dict_src:
        :return:
        """

        init_options = {
            "GroupId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
        }

        self.init_attrs(dict_src, init_options)

    def update_from_raw_response(self, dict_src):
        """
        Update self from raw server response.

        @param dict_src:
        @return:
        """

        init_options = {
            "GroupId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Generate create request.

        request = {"GroupName": self.name,
                   "Tags": self.tags}

        return request
        @return:
        """

        raise NotImplementedError()

    def generate_attach_policies_requests(self):
        """
        Attach policies request.

        return [
            {
                "PolicyArn": policy.arn,
                "GroupName": self.name
            }
            for policy in self.policies]


        @return:
        """
        raise NotImplementedError()