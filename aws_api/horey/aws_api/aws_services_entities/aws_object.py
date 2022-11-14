"""
A base class for working with aws objects - parsing, caching and initiation.
"""
import pdb
import re
import datetime
from enum import Enum

from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger
from horey.network.ip import IP

logger = get_logger()


class AwsObject:
    """
    Class to handle aws objets' base interaction.
    """

    # Regex for manipulating CamelCase attr names
    _FIRST_CAP_RE = re.compile("(.)([A-Z][a-z]+)")
    _ALL_CAP_RE = re.compile("([a-z0-9])([A-Z])")
    #'2017-07-26 15:54:10.000000+0000'
    _DATE_MICROSECONDS_FORMAT_RE = re.compile(
        "([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})\.([0-9]{6})\+([0-9]{4})"
    )
    SELF_CACHED_TYPE_KEY_NAME = "horey_cached_type"

    def __init__(self, dict_src, from_cache=False):
        if from_cache:
            self.dict_src = None
        else:
            self.dict_src = dict_src
        self.name = None
        self.id = None
        self.tags = None
        self._region = None

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
                self.init_horey_cached_type(key_src, value)
            elif key_src in dict_options:
                dict_options[key_src](key_src, value)
            else:
                self.init_default_attr(key_src, value)

    def init_horey_cached_type(self, attr_name, value):
        """
        Init automatically cached values
        @param attr_name:
        @param value: {self.SELF_CACHED_TYPE_KEY_NAME: datetime/region/ip..., "value": value_to_init}
        @return:
        """

        if value.get(self.SELF_CACHED_TYPE_KEY_NAME) == "datetime":
            # Example: datetime.datetime.strptime('2017-07-26 15:54:10.000000+0000', '%Y-%m-%d %H:%M:%S.%f%z')
            new_value = datetime.datetime.strptime(
                value["value"], "%Y-%m-%d %H:%M:%S.%f%z"
            )
        elif value.get(self.SELF_CACHED_TYPE_KEY_NAME) == "ip":
            new_value = IP(value["value"], from_dict=True)
        elif value.get(self.SELF_CACHED_TYPE_KEY_NAME) == "region":
            inited_region = Region()
            inited_region.init_from_dict(value["value"])

            new_value = Region.get_region(inited_region.region_mark)
            if inited_region.region_name is not None:
                if new_value.region_name is not None:
                    if new_value.region_name != inited_region.region_name:
                        raise ValueError(
                            f"{new_value.region_name} != {inited_region.region_name}"
                        )
                else:
                    new_value.region_name = inited_region.region_name
        else:
            raise ValueError(f"{attr_name} : {value}")

        self.init_default_attr(attr_name, new_value)

    @property
    def h_class_name(self):
        """
        Used to init the object from cache.
        :return:
        """
        return self.__class__.__name__

    # pylint: disable=R0201
    @h_class_name.setter
    def h_class_name(self, _):
        """
        Should not be set explicitly.
        :param _:
        :return:
        """
        raise Exception("System parameter, can't set")

    @property
    def name(self):
        """
        Object specific name
        :return:
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Name setter
        :param value:
        :return:
        """
        self._name = value

    @property
    def id(self):
        """
        Object specific ID
        :return:
        """
        return self._id

    @id.setter
    def id(self, value):
        """
        ID setter
        :param value:
        :return:
        """
        self._id = value

    def init_default_attr(self, attr_name, value, formatted_name=None):
        """
        The default function to init an attribute received in AWS API call reply.
        :param attr_name:
        :param value:
        :param formatted_name:
        :return:
        """
        if formatted_name is None:
            formatted_name = self.format_attr_name(attr_name)
        setattr(self, formatted_name, value)

    def init_date_attr_from_formatted_string(
        self, attr_name, value, custom_format=None
    ):
        """
        "%Y-%m-%d %H:%M:%S.%f%z"

        :param attr_name:
        :param value:
        :param custom_format:
        :return:
        """
        if not value:
            return

        string_format = custom_format or "%Y-%m-%d %H:%M:%S.%f%z"

        datetime_object = datetime.datetime.strptime(value, string_format)
        self.init_default_attr(attr_name, datetime_object)

    def init_attrs(self, dict_src, dict_options, raise_on_no_option=False):
        """
        Init the object attributes according to given "recipe"
        :param dict_src:
        :param dict_options:
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
                        line_to_add = '"{}":  self.init_default_attr,'.format(key_src_)
                        composed_errors.append(line_to_add)
                        logger.error(line_to_add)

                if not raise_on_no_option:
                    self.init_default_attr(key_src, value)
                    continue

                print("\n".join(composed_errors))
                raise self.UnknownKeyError(
                    "\n".join(composed_errors)
                ) from caught_exception

    def update_attributes(self, dict_src):
        """
        Init self with all attributes using default init method.
        :param dict_src:
        :return:
        """
        for key_src, value in dict_src.items():
            self.init_default_attr(key_src, value)

    def format_attr_name(self, name):
        """
        # shamelessly copied from https://stackoverflow.com/a/1176023
        format_attr_name('CamelCase')
        'camel_case'
        format_attr_name('CamelCamelCase')
        'camel_camel_case'
        format_attr_name('Camel2Camel2Case')
        'camel2_camel2_case'
        format_attr_name('getHTTPResponseCode')
        'get_http_response_code'
        format_attr_name('get2HTTPResponseCode')
        'get2_http_response_code'
        format_attr_name('HTTPResponseCode')
        'http_response_code'
        format_attr_name('HTTPResponseCodeXYZ')
        'http_response_code_xyz'
        :param name:
        :return:
        """

        s1 = self._FIRST_CAP_RE.sub(r"\1_\2", name)
        s1 = s1.replace("__", "_")
        return self._ALL_CAP_RE.sub(r"\1_\2", s1).lower()

    def convert_to_dict(self):
        """
        Convert self to a cache dict
        :return:
        """
        return self.convert_to_dict_static(self.__dict__)

    @staticmethod
    def convert_to_dict_static(obj_src, custom_types=None):
        # pylint: disable=R0911
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
                ret[key] = AwsObject.convert_to_dict_static(
                    value, custom_types=custom_types
                )
            return ret

        if isinstance(obj_src, list):
            return [
                AwsObject.convert_to_dict_static(value, custom_types=custom_types)
                for value in obj_src
            ]

        if isinstance(obj_src, AwsObject):
            return obj_src.convert_to_dict()

        if isinstance(obj_src, datetime.datetime):
            return {
                AwsObject.SELF_CACHED_TYPE_KEY_NAME: "datetime",
                "value": obj_src.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            }

        if isinstance(obj_src, Region):
            return {
                AwsObject.SELF_CACHED_TYPE_KEY_NAME: "region",
                "value": obj_src.convert_to_dict(),
            }

        if isinstance(obj_src, IP):
            return {
                AwsObject.SELF_CACHED_TYPE_KEY_NAME: "ip",
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

    class UnknownKeyError(Exception):
        """
        If trying to access unknown key
        """

    class ParsingError(Exception):
        """
        Can't parse the object while initializing.
        """

    def get_tag(
        self,
        key,
        ignore_missing_tag=False,
        tag_key_specifier="Key",
        tag_value_specifier="Value",
    ):
        if self.tags is None:
            if ignore_missing_tag:
                return None
            raise RuntimeError("No tags associated")

        for tag in self.tags:
            tag_key_value = tag.get(tag_key_specifier)
            tag_key_value = (
                tag_key_value
                if tag_key_value is not None
                else tag.get(tag_key_specifier.lower())
            )

            if tag_key_value.lower() == key:
                tag_value_value = tag.get(tag_value_specifier)
                return (
                    tag_value_value
                    if tag_value_value is not None
                    else tag.get(tag_value_specifier.lower())
                )

        if ignore_missing_tag:
            return None

        raise RuntimeError(f"No tag '{key}' associated")

    def get_tagname(self, ignore_missing_tag=False):
        return self.get_tag("name", ignore_missing_tag=ignore_missing_tag)

    def print_dict_src(self):
        for key, value in self.dict_src.items():
            if isinstance(value, str):
                print(f'"{key}" : "{value}"')
                continue

            print(f"{key}: {value}")

    def print(self):
        for key, value in self.__dict__.items():
            if isinstance(value, str):
                print(f'"{key}" : "{value}"')
                continue

            print(f"{key}: {repr(value)}")

    @property
    def region(self):
        if self._region is not None:
            return self._region

        if self.arn is not None:
            self._region = Region.get_region(self.arn.split(":")[3])

        return self._region

    @region.setter
    def region(self, value):
        if isinstance(value, str):
            value = Region.get_region(value)

        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    class UndefinedStatusError(RuntimeError):
        """
        Status was not set
        """
