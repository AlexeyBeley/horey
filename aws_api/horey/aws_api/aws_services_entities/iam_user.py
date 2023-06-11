"""
Module to handle AWS IAM Users.
"""
from horey.aws_api.aws_services_entities.aws_object import AwsObject


class IamUser(AwsObject):
    """
    Class representing IAM user.
    """

    def __init__(self, dict_src, from_cache=False):
        """
        Init Iam user with boto3 dict
        :param dict_src:
        """
        super().__init__(dict_src)
        self.attached_policies = None
        self.policies = None
        self.groups = None
        self.permissions_boundary = None
        self.tags = None
        self.path = None

        if from_cache:
            self._init_user_from_cache(dict_src)
            return

        init_options = {
            "UserId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Path": self.init_default_attr,
            "UserName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "Arn": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "PasswordLastUsed": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_user_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {}

        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Update from server response.

        :param dict_src:
        :return:
        """

        init_options = {
            "UserId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Path": self.init_default_attr,
            "UserName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "Arn": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "PasswordLastUsed": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Generate create request.

        :return:
        """

        request = {"UserName": self.name,
                   "Tags": self.tags}

        if self.path is not None:
            request["Path"] = self.path

        if self.permissions_boundary is not None:
            request["PermissionsBoundary"] = self.permissions_boundary
        return request
