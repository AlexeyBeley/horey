"""
AWS GlueDatabase representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class GlueDatabase(AwsObject):
    """
    AWS GlueDatabase class
    https://docs.aws.amazon.com/glue/latest/dg/glue-specifying-resource-arns.html
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.create_time = None
        self.account_id = None
        self.catalog_id = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "CreateTime": self.init_default_attr,
            "CreateTableDefaultPermissions": self.init_default_attr,
            "CatalogId": self.init_default_attr,
            "Description": self.init_default_attr,
            "Parameters": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def arn(self):
        if self._arn is None:
            self._arn = f"arn:aws:glue:{self.region.region_mark}:{self.account_id}:database/{self.name}"
        return self._arn

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
        Standard
        :param dict_src:
        :return:
        """
        init_options = {
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "CreateTime": self.init_default_attr,
            "CreateTableDefaultPermissions": self.init_default_attr,
            "CatalogId": self.init_default_attr,
            "Description": self.init_default_attr,
            "Parameters": self.init_default_attr,
        }
        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard
        :return:
        """
        request = {"DatabaseInput": {"Name": self.name}}

        return request
