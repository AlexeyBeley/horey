"""
Module handling IAM role object
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class IamInstanceProfile(AwsObject):
    """Class representing AWS IAM Role"""

    def __init__(self, dict_src, from_cache=False):
        """
        Init Iam user with boto3 dict

        :param dict_src:
        """
        super().__init__(dict_src)

        if from_cache:
            self._init_instance_profile_from_cache(dict_src)
            return

        init_options = {
            "Path": self.init_default_attr,
            "InstanceProfileName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "InstanceProfileId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Arn": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "Roles": self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options, raise_on_no_option=True)

    def _init_instance_profile_from_cache(self, dict_src):
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
            "MaxSessionDuration": self.init_default_attr}

        self.init_attrs(dict_src, init_options)

    def update_from_raw_response(self, dict_src):
        init_options = {
            "MaxSessionDuration": self.init_default_attr}

        self.init_attrs(dict_src, init_options, raise_on_no_option=True)

    def generate_create_request(self):
        request = dict()
        request["RoleName"] = self.name
        request["Tags"] = self.tags

        return request

    def generate_add_role_requests(self):
        return [
            {
                "InstanceProfileName": self.name,
                "RoleName": role["RoleName"]
            }
            for role in self.roles]
