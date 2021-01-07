"""
Module handling IAM role object
"""
from aws_object import AwsObject


class IamRole(AwsObject):
    """Class representing AWS IAM Role"""
    def __init__(self, dict_src, from_cache=False):
        """
        Init Iam user with boto3 dict

        :param dict_src:
        """
        self.policies = []

        super().__init__(dict_src)

        if from_cache:
            self._init_iam_role_from_cashe(dict_src)
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

    def _init_iam_role_from_cashe(self, dict_src):
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
                        "RoleLastUsed": self.init_default_attr,
                        "Tags": self.init_default_attr,
                        "MaxSessionDuration": self.init_default_attr}

        self.init_attrs(dict_src, init_options)

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
