"""
Base class for all azure entities.

"""

import datetime
from enum import Enum
# pylint: disable= no-name-in-module
from horey.azure_api.base_entities.region import Region

from horey.h_logger import get_logger
from horey.network.ip import IP

logger = get_logger()


class AzureObject:
    """
    Main class.

    """
    SELF_CACHED_TYPE_KEY_NAME = "horey_cached_type"

    def __init__(self, dict_src, from_cache=False):
        if from_cache:
            self.dict_src = None
        else:
            self.dict_src = dict_src
        self.name = None
        self.id = None
        self._resource_group_name = None

    @property
    def resource_group_name(self):
        """
        Generate or use one explicitly set.

        :return:
        """

        if self._resource_group_name is None:
            if self.id is None:
                raise ValueError("Neither _resource_group_name nor id were set")
            lst_id = self.id.split("/")
            if lst_id[3] != "resourceGroups":
                raise RuntimeError(f"Can not parse ID: {lst_id}")
            self._resource_group_name = lst_id[4]

        return self._resource_group_name

    @resource_group_name.setter
    def resource_group_name(self, value):
        """
        Setter.

        :param value:
        :return:
        """

        self._resource_group_name = value

    def convert_to_dict(self):
        """
        Convert self to a cache dict
        :return:
        """
        return self.convert_to_dict_static(self.__dict__)

    # pylint: disable= too-many-return-statements, too-many-branches
    @staticmethod
    def convert_to_dict_static(obj_src, custom_types=None):
        """
        Converts all known attribute types to a specific form available to be init from cache.

        :param obj_src:
        :param custom_types: list of dicts: {type:converter_function}
        :return:
        """
        if type(obj_src) in [str, int, bool, type(None)]:
            return obj_src

        if isinstance(obj_src, dict):
            ret = {}
            for key, value in obj_src.items():
                if type(key) not in [int, str]:
                    raise ValueError(f"{key=}, {type(key)=}")
                ret[key] = AzureObject.convert_to_dict_static(
                    value, custom_types=custom_types
                )
            return ret

        if isinstance(obj_src, list):
            return [
                AzureObject.convert_to_dict_static(value, custom_types=custom_types)
                for value in obj_src
            ]

        if isinstance(obj_src, AzureObject):
            return obj_src.convert_to_dict()

        if isinstance(obj_src, datetime.datetime):
            return {
                AzureObject.SELF_CACHED_TYPE_KEY_NAME: "datetime",
                "value": obj_src.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            }

        if isinstance(obj_src, Region):
            return {
                AzureObject.SELF_CACHED_TYPE_KEY_NAME: "region",
                "value": obj_src.convert_to_dict(),
            }

        if isinstance(obj_src, IP):
            return {
                AzureObject.SELF_CACHED_TYPE_KEY_NAME: "ip",
                "value": obj_src.convert_to_dict(),
            }

        if isinstance(obj_src, Enum):
            return obj_src.value

        # In most cases it will become str
        # Ugly but efficient
        try:
            assert obj_src.convert_to_dict
            raise DeprecationWarning(
                f"'return obj_src.convert_to_dict()' Use the new SELF_CACHED_TYPE_KEY_NAME format: {obj_src}"
            )
        except AttributeError:
            pass

        if not custom_types:
            return str(obj_src)

        if type(obj_src) not in custom_types:
            return str(obj_src)

        return custom_types[type(obj_src)](obj_src)

    def init_default_attr(self, attr_name, value, formatted_name=None):
        """
        The default function to init an attribute received in AWS API call reply.
        :param attr_name:
        :param value:
        :param formatted_name:
        :return:
        """
        if formatted_name is None:
            formatted_name = attr_name
        setattr(self, formatted_name, value)

    def init_attrs(self, dict_src, dict_options, raise_on_no_option=False):
        """
        Init the object attributes according to given "recipe"

        @param dict_src:
        @param dict_options:
        @param raise_on_no_option: If key not set explicitly raise exception.
        :return:
        """

        composed_errors = []
        for key_src, value in dict_src.items():
            try:
                dict_options[key_src](key_src, value)
            except KeyError as caught_exception:
                for key_src_ in dict_src:
                    if key_src_ not in dict_options:
                        line_to_add = f'"{key_src_}":  self.init_default_attr,'
                        logger.warning(f"{self.__class__.__name__}: {line_to_add}")
                        composed_errors.append(line_to_add)

                if not raise_on_no_option:
                    self.init_default_attr(key_src, value)
                    continue

                print("\n".join(composed_errors))
                raise self.UnknownKeyError(
                    "\n".join(composed_errors)
                ) from caught_exception

    def _init_from_cache(self, dict_src, dict_options):
        """
        Init aws object from cache.

        :param dict_src:
        :param dict_options:
        :return:
        """

        for key_src, value in dict_src.items():
            if (
                isinstance(value, dict)
                and value.get(self.SELF_CACHED_TYPE_KEY_NAME) is not None
            ):
                raise NotImplementedError()
            if key_src in dict_options:
                dict_options[key_src](key_src, value)
            else:
                self.init_default_attr(key_src, value)

    class UnknownKeyError(Exception):
        """
        If trying to access unknown key
        """
