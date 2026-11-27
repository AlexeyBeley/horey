"""
Module handling AWS object
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class IamInstanceProfile(AwsObject):
    """Class representing AWS IAM Instance profile"""

    def __init__(self, dict_src, from_cache=False):
        """
        Init Iam user with boto3 dict

        :param dict_src:
        """
        super().__init__(dict_src)
        self.path = None
        self.roles = []

        if from_cache:
            self._init_instance_profile_from_cache(dict_src)
            return

        self.update_from_raw_response(dict_src)

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

        init_options = {"MaxSessionDuration": self.init_default_attr}

        self.init_attrs(dict_src, init_options)

    def update_from_raw_response(self, dict_src):
        """
        From API response dict.

        :param dict_src:
        :return:
        """

        init_options = {
            "Path": self.init_default_attr,
            "InstanceProfileName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "InstanceProfileId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Arn": self.init_default_attr,
            "CreateDate": self.init_default_attr,
            "Roles": self.init_default_attr,
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"InstanceProfileName": self.name}
        self.extend_request_with_required_parameters(request, ["Tags", "Path"])

        return request

    def generate_add_role_requests(self):
        """
        Standard.

        :return:
        """
        return [
            {"InstanceProfileName": self.name, "RoleName": role["RoleName"]}
            for role in self.roles
        ]
