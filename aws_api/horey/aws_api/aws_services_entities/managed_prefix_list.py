"""
AWS Lambda representation
"""
import pdb

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class ManagedPrefixList(AwsObject):
    """
    Elasticsearch domain class
    """
    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []
        self.entries = []
        self.associations = []
        self.arn = None
        self.version = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return
        init_options = {
            "PrefixListId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "AddressFamily": self.init_default_attr,
            "State": self.init_default_attr,
            "PrefixListArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "PrefixListName": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "MaxEntries": self.init_default_attr,
            "Version": self.init_default_attr,
            "Tags": self.init_default_attr,
            "OwnerId": self.init_default_attr,
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

    def add_entry_from_raw_response(self, raw_value):
        entry = self.Entry(raw_value)
        self.entries.append(entry)

    def add_association_from_raw_response(self, raw_value):
        entry = self.Association(raw_value)
        self.associations.append(entry)

    @property
    def region(self):
        if self.arn is None:
            raise ValueError("ARN must be set")
        return self.arn.split(":")[3]

    def get_entries_add_request(self, dst_managed_prefix_list):
        request_entries = []
        self_cidr_descriptions = {entry.cidr: entry.description for entry in self.entries}
        for dst_managed_prefix_list_entry in dst_managed_prefix_list.entries:
            if dst_managed_prefix_list_entry.cidr not in self_cidr_descriptions or \
            dst_managed_prefix_list_entry.description != self_cidr_descriptions[dst_managed_prefix_list_entry.cidr]:
                request_entries.append({
                "Cidr": dst_managed_prefix_list_entry.cidr,
                "Description": dst_managed_prefix_list_entry.description
                })

        if len(request_entries) == 0:
            return None

        request = {
            "CurrentVersion": self.version,
            "PrefixListId": self.id,
            "AddEntries": request_entries
        }
        return request

    class Entry(AwsObject):
        def __init__(self, dict_src, from_cache=False):
            super().__init__(dict_src)
            self.instances = []

            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            init_options = {
                "Cidr": self.init_default_attr,
                "Description": self.init_default_attr,
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

    class Association(AwsObject):
        def __init__(self, dict_src, from_cache=False):
            super().__init__(dict_src)
            self.instances = []

            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            init_options = {
                "ResourceId": self.init_default_attr,
                "ResourceOwner": self.init_default_attr,
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