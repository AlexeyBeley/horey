"""
AWS ECR Repo representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ECRRepository(AwsObject):
    """
    Main class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.policy_text = None

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

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        request = {"repositoryName": self.name, "tags": self.tags}
        return request

    def generate_change_repository_policy_requests(self, desired_state):
        """
        Standard.

        :param desired_state:
        :return: create, delete
        """
        if self.policy_text == desired_state.policy_text:
            return None, None

        dict_ret = {"repositoryName": desired_state.name}

        if desired_state.policy_text:
            dict_ret.update({"policyText": desired_state.policy_text})
            return dict_ret, None

        return None, dict_ret

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """
        request = {"repositoryName": self.name, "force": True}
        return request

    def update_from_raw_response(self, dict_src):
        """
        Standard.

        :param dict_src:
        :return:
        """
        init_options = {
            "repositoryArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "registryId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "repositoryName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "repositoryUri": self.init_default_attr,
            "createdAt": self.init_default_attr,
            "imageTagMutability": self.init_default_attr,
            "imageScanningConfiguration": self.init_default_attr,
            "encryptionConfiguration": self.init_default_attr,
            "policyText": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)
