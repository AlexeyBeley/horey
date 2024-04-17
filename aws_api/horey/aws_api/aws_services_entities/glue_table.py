"""
AWS Glue Tabale representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class GlueTable(AwsObject):
    """
    AWS GlueTable class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.create_time = None
        self.parameters = None
        self.partition_keys = None
        self.database_name = None
        self.account_id = None
        self.description = None
        self.retention = None
        self.storage_descriptor = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "DatabaseName": self.init_default_attr,
            "Owner": self.init_default_attr,
            "CreateTime": self.init_default_attr,
            "UpdateTime": self.init_default_attr,
            "LastAccessTime": self.init_default_attr,
            "Retention": self.init_default_attr,
            "StorageDescriptor": self.init_default_attr,
            "PartitionKeys": self.init_default_attr,
            "TableType": self.init_default_attr,
            "Parameters": self.init_default_attr,
            "CreatedBy": self.init_default_attr,
            "IsRegisteredWithLakeFormation": self.init_default_attr,
            "CatalogId": self.init_default_attr,
            "Description": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    @property
    def arn(self):
        """
        Maually generate arn
        :return:
        """
        if self._arn is None:
            self._arn = f"arn:aws:glue:{self.region.region_mark}:{self.account_id}:table/{self.database_name}/{self.name}"
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
            "DatabaseName": self.init_default_attr,
            "Owner": self.init_default_attr,
            "CreateTime": self.init_default_attr,
            "UpdateTime": self.init_default_attr,
            "LastAccessTime": self.init_default_attr,
            "Retention": self.init_default_attr,
            "StorageDescriptor": self.init_default_attr,
            "PartitionKeys": self.init_default_attr,
            "TableType": self.init_default_attr,
            "Parameters": self.init_default_attr,
            "CreatedBy": self.init_default_attr,
            "IsRegisteredWithLakeFormation": self.init_default_attr,
            "CatalogId": self.init_default_attr,
            "Description": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard
        :return:
        """
        request = {"DatabaseName": self.database_name,
                   "TableInput": {}}
        request["TableInput"]["Name"] = self.name
        request["TableInput"]["Description"] = self.description
        request["TableInput"]["Retention"] = self.retention

        request["TableInput"]["StorageDescriptor"] = self.storage_descriptor
        if self.parameters is not None:
            request["TableInput"]["Parameters"] = self.parameters
        if self.partition_keys is not None:
            request["TableInput"]["PartitionKeys"] = self.partition_keys

        return request
