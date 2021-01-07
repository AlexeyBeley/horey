"""
Module to handle AWS IAM access key
"""
from aws_object import AwsObject


class IamAccessKey(AwsObject):
    """
    Class representing AWS IAM Access key
    """
    def __init__(self, dict_src):
        """
        Init Iam Access Key with boto3 dict
        :param dict_src:
        """
        super().__init__(dict_src)

        init_options = {
                        "AccessKeyId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
                        "UserName": self.init_default_attr,
                        "Status": self.init_default_attr,
                        "CreateDate": self.init_default_attr}

        self.init_attrs(dict_src, init_options)
