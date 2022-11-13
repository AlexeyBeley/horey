"""
Class to represent ec2 spot fleet request
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


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
        self._region = None

        if from_cache:
            self._init_ec2_launch_template_from_cache(dict_src)
            return

        init_options = {
            "LaunchTemplateName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "CreateTime": self.init_default_attr,
            "CreatedBy": self.init_default_attr,
            "DefaultVersionNumber": self.init_default_attr,
            "LatestVersionNumber": self.init_default_attr,
            "LaunchTemplateId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Tags": self.init_default_attr,
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

    def generate_create_request(self):
        request = dict()
        request["LaunchTemplateName"] = self.name
        request["LaunchTemplateData"] = self.launch_template_data
        request["TagSpecifications"] = [
            {"ResourceType": "launch-template", "Tags": self.tags},
        ]
        return request

    def generate_modify_launch_template_request(self, version):
        request = dict()
        request["LaunchTemplateName"] = self.name
        request["DefaultVersion"] = version
        return request

    def generate_dispose_request(self):
        request = dict()
        request["LaunchTemplateName"] = self.name
        request["DryRun"] = False
        return request

    def update_from_raw_response(self, dict_src):
        init_options = {
            "LaunchTemplateName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "CreateTime": self.init_default_attr,
            "CreatedBy": self.init_default_attr,
            "DefaultVersionNumber": self.init_default_attr,
            "LatestVersionNumber": self.init_default_attr,
            "LaunchTemplateId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def region(self):
        if self._region is not None:
            return self._region

        raise ValueError()

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
