"""
Class to represent ec2 spot fleet request
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class EC2LaunchTemplate(AwsObject):
    """
    Class to represent ec2 launch template
    """

    def __init__(self, dict_src, from_cache=False):
        """
        Init EC2 launch template with boto3 dict
        :param dict_src:
        """
        super().__init__(dict_src)

        if from_cache:
            self._init_ec2_launch_template_from_cache(dict_src)
            return

        init_options = {
            "LaunchTemplateName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "CreateTime": self.init_default_attr,
            "CreatedBy": self.init_default_attr,
            "DefaultVersionNumber": self.init_default_attr,
            "LatestVersionNumber": self.init_default_attr,
            "LaunchTemplateId": self.init_default_attr,
            "Tags": self.init_default_attr
        }

        self.init_attrs(dict_src, init_options)

    def _init_ec2_launch_template_from_cache(self, dict_src):
        """
        Init self from preserved dict.
        :param dict_src:
        :return:
        """
        options = {}

        self._init_from_cache(dict_src, options)
