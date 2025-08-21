"""
AWS Lambda representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ECRImage(AwsObject):
    """
    AWS VPC class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.image_tags = None
        self.last_recorded_pull_time = None
        self.image_pushed_at = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "registryId": self.init_default_attr,
            "repositoryName": self.init_default_attr,
            "imageDigest": self.init_default_attr,
            "imageTags": self.init_default_attr,
            "imageSizeInBytes": self.init_default_attr,
            "imagePushedAt": self.init_default_attr,
            "imageScanStatus": self.init_default_attr,
            "imageScanFindingsSummary": self.init_default_attr,
            "imageManifestMediaType": self.init_default_attr,
            "artifactMediaType": self.init_default_attr,
            "lastRecordedPullTime": self.init_default_attr,
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
