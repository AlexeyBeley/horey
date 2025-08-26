"""
AWS Lambda representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class BackupsRecoveryPoint(AwsObject):
    """
    AWS ACMCertificate class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)

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
        Update self from raw server response.

        @param dict_src:
        @return:
        """

        init_options = {
            "CertificateArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "DomainName": self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options)
