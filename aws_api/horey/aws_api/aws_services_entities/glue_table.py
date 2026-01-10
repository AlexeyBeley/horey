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

        self.update_attributes(dict_src)

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
            "VersionId":  self.init_default_attr,
            "IsMultiDialectView": self.init_default_attr,
            "IsMaterializedView": self.init_default_attr,
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

    def generate_tagging_requests(self, desired_state):
        """
        Generate create tags and delete tags requests.

        client.untag_resource(
        ResourceArn='string',
        TagsToRemove=[
        'string',
        ]
        )

        response = client.tag_resource(
       ResourceArn='string',
        TagsToAdd={
        'string': 'string'
        }
        )

        :param desired_state:
        :return:
        """

        if self.tags == desired_state.tags:
            return None, None

        self_tags = self.tags or {}
        desired_tags = desired_state.tags or {}
        add_tags = {tag_key: tag_value for tag_key, tag_value in desired_tags.items() if self_tags.get(tag_key) != tag_value}
        remove_tags = [tag_key for tag_key, tag_value in self_tags.items() if desired_tags.get(tag_key) != tag_value]

        add_request = None if not add_tags else {"ResourceArn": self.arn, "TagsToAdd": add_tags}
        remove_request = None if not remove_tags else {"ResourceArn": self.arn, "TagsToRemove": remove_tags}
        return add_request, remove_request


    def generate_update_table_request(self, desired_state):
        """
        Generate update table request.

        :param desired_state:
        :return:
        """

        self_create_request = self.generate_create_request()
        desired_create_request = desired_state.generate_create_request()
        for key, value in self_create_request["TableInput"].items():
            if desired_create_request["TableInput"].get(key) != value:
                return desired_create_request

        return None
