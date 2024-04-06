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
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

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

    def generate_create_request(self):
        """
        Standard.

        :return:
        """
        request = {"repositoryName": self.name, "tags": self.tags}
        return request

    def generate_dispose_request(self):
        """
        Standard.

        :return:
        """
        request = {"repositoryName": self.name, "force": True}
        return request

    def update_from_raw_create(self, dict_src):
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
        }

        self.init_attrs(dict_src, init_options)
