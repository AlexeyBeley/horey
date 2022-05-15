"""
Module handling IAM role object
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class IamRole(AwsObject):
    """Class representing AWS IAM Role"""

    def __init__(self, dict_src, from_cache=False):
        """
        Init Iam user with boto3 dict

        :param dict_src:
        """
        self.policies = []
        self.role_last_used_time = None
        self.role_last_used_region = None

        super().__init__(dict_src)

        if from_cache:
            self._init_iam_role_from_cache(dict_src)
            return

        init_options = {
            "RoleId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Path": self.init_default_attr,
            "RoleName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Arn": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "AssumeRolePolicyDocument": self.init_default_attr,
            "Description": self.init_default_attr,
            "MaxSessionDuration": self.init_default_attr}
        self.init_attrs(dict_src, init_options)

    def _init_iam_role_from_cache(self, dict_src):
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
            "RoleId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Path": self.init_default_attr,
            "RoleName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Arn": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "AssumeRolePolicyDocument": self.init_default_attr,
            "Description": self.init_default_attr,
            "RoleLastUsed": self.init_role_last_used_attr,
            "Tags": self.init_default_attr,
            "MaxSessionDuration": self.init_default_attr}

        self.init_attrs(dict_src, init_options)

    def init_role_last_used_attr(self, _, dict_src):
        """
        Init RoleLastUsed - split to time and region

        @param _:
        @param dict_src:
        @return:
        """
        if not dict_src:
            return
        for key in dict_src:
            if key == "LastUsedDate":
                self.role_last_used_time = dict_src.get(key)
            elif key == "Region":
                self.role_last_used_region = Region.get_region(dict_src.get(key))
            else:
                raise NotImplementedError(key)

    def add_policy(self, policy):
        """
        Add single AWS Iam Policy.
        :param policy:
        :return:
        """
        self.policies.append(policy)

    def init_assume_role_policy_document(self, key, value):
        """
        Init assume role from AWS API response.
        :param key:
        :param value:
        :return:
        """
        raise NotImplementedError("Not yet implemented, replaced pdb.set_trace")

    def update_from_raw_response(self, dict_src):
        init_options = {
            "RoleId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Path": self.init_default_attr,
            "RoleName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "Arn": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "AssumeRolePolicyDocument": self.init_default_attr,
            "Description": self.init_default_attr,
            "MaxSessionDuration": self.init_default_attr}

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        request = dict()
        request["RoleName"] = self.name
        request["Description"] = self.description
        request["AssumeRolePolicyDocument"] = self.assume_role_policy_document
        request["MaxSessionDuration"] = self.max_session_duration
        request["Tags"] = self.tags

        return request

    def generate_attach_policies_requests(self, desired_role=None):
        return [
            {
                "PolicyArn": policy.arn,
                "RoleName": self.name
            }
            for policy in self.policies]
