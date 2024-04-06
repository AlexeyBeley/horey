"""
AWS Lambda representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class ManagedPrefixList(AwsObject):
    """
    Elasticsearch domain class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self.instances = []
        self.entries = []
        self.associations = []
        self.max_entries = None
        self.address_family = None
        self.version = None
        self._region = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "PrefixListId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "AddressFamily": self.init_default_attr,
            "State": self.init_default_attr,
            "PrefixListArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "PrefixListName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "MaxEntries": self.init_default_attr,
            "Version": self.init_default_attr,
            "Tags": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "StateMessage": self.init_default_attr,
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
        """
        Add entry from raw server response.

        @param raw_value:
        @return:
        """

        entry = self.Entry(raw_value)
        self.entries.append(entry)

    def add_association_from_raw_response(self, raw_value):
        """
        Add association from raw server response.

        @param raw_value:
        @return:
        """

        entry = self.Association(raw_value)
        self.associations.append(entry)

    @property
    def region(self):
        """
        Self region generator.

        @return:
        """

        if self.arn is not None:
            return Region.get_region(self.arn.split(":")[3])
        return self._region

    @region.setter
    def region(self, value):
        """
        Self region setter

        @param value:
        @return:
        """

        if self.arn is not None:
            raise ValueError("Can not explicitly set region when arn is set")
        if not isinstance(value, Region):
            raise ValueError(value)
        self._region = value

    def get_entries_modify_request(self, managed_prefix_list, declarative):
        """
        Generate modifying request.

        @param managed_prefix_list:
        @param declarative: Remove undesired entries.
        @return:
        """

        if not declarative:
            return self.get_entries_add_request(managed_prefix_list)

        return self.get_entries_add_remove_request(managed_prefix_list)

    def get_entries_add_request(self, dst_managed_prefix_list):
        """
        Only add entries - do not remove.

        @param dst_managed_prefix_list:
        @return:
        """

        request_entries = []
        self_cidr_descriptions = {
            entry.cidr: entry.description for entry in self.entries
        }
        for dst_managed_prefix_list_entry in dst_managed_prefix_list.entries:
            if (
                    dst_managed_prefix_list_entry.cidr not in self_cidr_descriptions
                    or dst_managed_prefix_list_entry.description
                    != self_cidr_descriptions[dst_managed_prefix_list_entry.cidr]
            ):
                request_entries.append(
                    {
                        "Cidr": dst_managed_prefix_list_entry.cidr,
                        "Description": dst_managed_prefix_list_entry.description,
                    }
                )

        if len(request_entries) == 0:
            return None

        request = {
            "CurrentVersion": self.version,
            "PrefixListId": self.id,
            "AddEntries": request_entries,
        }
        return request

    def get_entries_add_remove_request(self, desired_prefix_list):
        """
        Get declarative modifying request.

        @param desired_prefix_list:
        @return:
        """

        request_entries_add = []
        request_entries_remove = []

        for dst_managed_prefix_list_entry in desired_prefix_list.entries:
            found = False
            for entry in self.entries:
                if (
                        dst_managed_prefix_list_entry.cidr == entry.cidr
                        or dst_managed_prefix_list_entry.description == entry.description
                ):
                    if (
                            dst_managed_prefix_list_entry.cidr != entry.cidr
                            or dst_managed_prefix_list_entry.description
                            != entry.description
                    ):
                        request_entries_remove.append({"Cidr": entry.cidr})
                    else:
                        found = True

            if not found:
                request_entries_add.append(
                    {
                        "Cidr": dst_managed_prefix_list_entry.cidr,
                        "Description": dst_managed_prefix_list_entry.description,
                    }
                )

        if len(request_entries_add) == 0:
            return None

        request = {
            "CurrentVersion": self.version,
            "PrefixListId": self.id,
            "AddEntries": request_entries_add,
            "RemoveEntries": request_entries_remove,
        }
        return request

    def generate_create_request(self):
        """
        Generate creation request

        @return:
        """

        request = {
            "PrefixListName": self.name,
            "MaxEntries": self.max_entries,
            "AddressFamily": self.address_family,
            "TagSpecifications": [{"ResourceType": "prefix-list", "Tags": self.tags}],
            "Entries": [
                {"Cidr": entry.cidr, "Description": entry.description}
                for entry in self.entries
            ],
        }

        return request

    def update_from_raw_create(self, dict_src):
        """
        Update self information from raw server reply.

        @param dict_src:
        @return:
        """

        init_options = {
            "PrefixListId": lambda x, y: self.init_default_attr(
                x, y, formatted_name="id"
            ),
            "AddressFamily": self.init_default_attr,
            "State": self.init_default_attr,
            "PrefixListArn": lambda x, y: self.init_default_attr(
                x, y, formatted_name="arn"
            ),
            "PrefixListName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "MaxEntries": self.init_default_attr,
            "Version": self.init_default_attr,
            "Tags": self.init_default_attr,
            "OwnerId": self.init_default_attr,
            "StateMessage": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    class Entry(AwsObject):
        """
        Entry representation

        """

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
        """
        Association representation class

        """

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
