"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class AMI(AwsObject):
    """
    AWS AvailabilityZone class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "ImageId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "Architecture": self.init_default_attr,
            "CreationDate": lambda x, y: self.init_date_attr_from_formatted_string(x, y, custom_format="%Y-%m-%dT%H:%M:%S.%f%Z"),
            "ImageLocation": self.init_default_attr,
            "ImageType": self.init_default_attr,
            "Public": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "PlatformDetails": self.init_default_attr,
            "UsageOperation": self.init_default_attr,
            "State": self.init_default_attr,
            "BlockDeviceMappings": self.init_default_attr,
            "Hypervisor": self.init_default_attr,
            "RootDeviceType": self.init_default_attr,
            "VirtualizationType": self.init_default_attr,
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

    def update_value_from_raw_response(self, raw_value):
        pdb.set_trace()
