"""
AWS Lambda representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class KMSKey(AwsObject):
    """
    AWS KMSKey class
    """

    def __init__(self, dict_src, from_cache=False):
        super().__init__(dict_src)
        self._region = None
        self.aliases = []
        self.key_usage = None
        self.description = None
        self.enabled = None
        self.key_manager = None

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "KeyArn": lambda x, y: self.init_default_attr(x, y, formatted_name="arn"),
            "KeyId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
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

    def update_from_raw_response(self, dict_src):
        """
        Update attributes from raw server response.

        :param dict_src:
        :return:
        """

        self.dict_src = dict_src

        init_options = {
            "KeyId": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
            "AWSAccountId": self.init_default_attr,
            "Arn": self.init_default_attr,
            "CreationDate": self.init_default_attr,
            "Enabled": self.init_default_attr,
            "Description": self.init_default_attr,
            "KeyUsage": self.init_default_attr,
            "KeyState": self.init_default_attr,
            "Origin": self.init_default_attr,
            "KeyManager": self.init_default_attr,
            "CustomerMasterKeySpec": self.init_default_attr,
            "EncryptionAlgorithms": self.init_default_attr,
            "MultiRegion": self.init_default_attr,
            "KeySpec": self.init_default_attr,
            "CurrentKeyMaterialId": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def update_from_list_tags_response(self, dict_src):
        """
        Update tags from raw server response.

        :param dict_src:
        :return:
        """

        init_options = {
            "Tags": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def update_from_list_aliases_response(self, dict_src):
        """
        Update aliases from raw server response.

        :param dict_src:
        :return:
        """

        init_options = {
            "Aliases": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard.

        :return:
        """

        request = {"KeyUsage": self.key_usage, "Description": self.description, "Tags": self.tags}

        return request

    def generate_schedule_key_deletion_request(self, days):
        """
        Standard.

        :return:
        """

        request = {"KeyId": self.id, "PendingWindowInDays": days}

        return request

    # pylint: disable=too-many-branches
    def generate_alias_provision_requests(self, target):
        """
        Delete aliases if needed. Create aliases.

        :param target:
        :return:
        """
        name = target.get_tag("name", tag_key_specifier="TagKey", tag_value_specifier="TagValue",
                              ignore_missing_tag=True)
        if name is None:
            raise ValueError("Missing Tag 'name'")
        alias_name = f"alias/{name}"

        found = False
        for target_alias in target.aliases:
            if not target_alias["AliasName"].startswith("alias/"):
                raise ValueError(f"Alias must start with 'alias/' prefix. Received: '{target_alias['AliasName']}'")
            if target_alias["AliasName"] == alias_name:
                found = True
        if not found:
            raise ValueError(f"Required alias '{alias_name}' is missing. Add: " + "{" + f'"AliasName": "{alias_name}"' +
                             "}")

        create_requests = []
        for target_alias in target.aliases:
            for self_alias in self.aliases:
                if self_alias["AliasName"] == target_alias["AliasName"]:
                    break
            else:
                create_requests.append({"AliasName": target_alias["AliasName"], "TargetKeyId": self.id})

        del_requests = []
        for self_alias in self.aliases:
            for target_alias in target.aliases:
                if self_alias["AliasName"] == target_alias["AliasName"]:
                    break
            else:
                del_requests.append({"AliasName": self_alias["AliasName"]})

        return del_requests, create_requests

    def generate_tag_resource_request(self, desired_key):
        """
        Standard.
        response = client.tag_resource(
        KeyId='string',
        Tags=[
            {
            'TagKey': 'string',
            'TagValue': 'string'
                },
            ]
            )

        :param desired_key:
        :return:
        """

        if self.generate_tags_dict() == desired_key.generate_tags_dict():
            return None
        return {"KeyId": self.id, "Tags": desired_key.tags}

    def generate_tags_dict(self):
        """
        Generate key:value dict for tags.

        :return:
        """

        # pylint: disable= not-an-iterable
        return {tag["TagKey"]: tag["TagValue"] for tag in self.tags}

    @property
    def region(self):
        """
        Standard.

        :return:
        """

        if self._region is not None:
            return self._region
        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        """
        Standard.

        :return:
        """

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value
