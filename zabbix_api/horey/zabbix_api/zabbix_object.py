from horey.common_utils.common_re_utils import CommonREUtils
from horey.common_utils.common_utils import CommonUtils
import datetime
from enum import Enum

from horey.h_logger import get_logger

logger = get_logger()


class ZabbixObject:
    SELF_CACHED_TYPE_KEY_NAME = "horey_cached_type"

    def __init__(self, dict_src, from_cache=False):
        if from_cache:
            self.dict_src = None
        else:
            self.dict_src = dict_src
        self.name = None
        self.common_re_utils = CommonREUtils()

    def convert_to_dict(self):
        """
        Convert self to a cache dict
        :return:
        """
        return self.convert_to_dict_static(self.__dict__)

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
                    raise Exception
                ret[key] = ZabbixObject.convert_to_dict_static(
                    value, custom_types=custom_types
                )
            return ret

        if isinstance(obj_src, list):
            return [
                ZabbixObject.convert_to_dict_static(value, custom_types=custom_types)
                for value in obj_src
            ]

        if isinstance(obj_src, ZabbixObject):
            return obj_src.convert_to_dict()

        if isinstance(obj_src, datetime.datetime):
            return {
                ZabbixObject.SELF_CACHED_TYPE_KEY_NAME: "datetime",
                "value": obj_src.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
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
            formatted_name = self.common_re_utils.pascal_case_case_to_snake_case(
                attr_name
            )

        setattr(self, formatted_name, value)

    def init_attrs(self, dict_src, raise_on_no_option=True):
        """
        Init the object attributes according to given "recipe"
        :param dict_src:
        :param dict_options:
        @param raise_on_no_option: If key not set explicitly raise exception.
        :return:
        """

        return CommonUtils.init_from_api_dict(self, dict_src, validate_attributes=raise_on_no_option)

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
            elif key_src in dict_options:
                dict_options[key_src](key_src, value)
            else:
                self.init_default_attr(key_src, value)

    class UnknownKeyError(Exception):
        """
        If trying to access unknown key
        """
