"""
AWS specific object representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class SecretsManagerSecret(AwsObject):
    """
    SecretsManager Secret class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.secret_string = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "ARN": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "Name": self.init_default_attr,
            "LastChangedDate": self.init_default_attr,
            "LastAccessedDate": self.init_default_attr,
            "Tags": self.init_default_attr,
            "SecretVersionsToStages": self.init_default_attr,
            "CreatedDate": self.init_default_attr,
            "VersionId": self.init_default_attr,
            "SecretString": self.init_default_attr,
            "VersionStages": self.init_default_attr,
            "ResponseMetadata": self.init_null,
        }

        self.init_attrs(dict_src, init_options)

    def init_null(self, _1, _2):
        """
        Place holder.

        :param _1:
        :param _2:
        :return:
        """

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_value_from_raw_response(self, raw_value):
        """
        Standard

        :param raw_value:
        :return:
        """
        self.secret_string = raw_value["SecretString"]
