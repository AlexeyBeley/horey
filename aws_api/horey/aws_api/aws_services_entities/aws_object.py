"""
A base class for working with aws objects - parsing, caching and initiation.
"""
import re
import datetime
from enum import Enum


class AwsObject:
    """
    Class to handle aws objets' base interaction.
    """

    # Regex for manipulating CamelCase attr names
    _FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
    _ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')

    def __init__(self, dict_src, from_cache=False):
        if from_cache:
            self.dict_src = None
        else:
            self.dict_src = dict_src
        self.name = None
        self.id = None

    def _init_from_cache(self, dict_src, dict_options):
        """
        Init aws object from cache.

        :param dict_src:
        :param dict_options:
        :return:
        """
        for key_src, value in dict_src.items():
            if key_src in dict_options:
                dict_options[key_src](key_src, value)
            else:
                self.init_default_attr(key_src, value)

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

    def init_date_attr_from_formatted_string(self, attr_name, value):
        """
        "%Y-%m-%d %H:%M:%S.%f%z"

        :param attr_name:
        :param value:
        :return:
        """

        datetime_object = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f%z")
        self.init_default_attr(attr_name, datetime_object)

    def init_date_attr_from_cache_string(self, attr_name, value):
        """
        Standard date format to be inited from cache. The format is set explicitly while cached.
        :param attr_name:
        :param value:
        :return:
        """
        if "+" not in value:
            raise NotImplementedError
        # To use %z : "2017-07-26 15:54:10+01:00" -> "2017-07-26 15:54:10+0100"
        index = value.rfind(":")
        value = value[:index] + value[index+1:]

        # Example: strptime('2017-07-26 15:54:10+0000', '%Y-%m-%d %H:%M:%S%z')
        datetime_object = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S%z")
        setattr(self, attr_name, datetime_object)

    def init_attrs(self, dict_src, dict_options):
        """
        Init the object attributes according to given "recipe"
        :param dict_src:
        :param dict_options:
        :return:
        """
        for key_src, value in dict_src.items():
            try:
                dict_options[key_src](key_src, value)
            except KeyError as caught_exception:
                for key_src_, _ in dict_src.items():
                    if key_src_ not in dict_options:
                        print('"{}":  self.init_default_attr,'.format(key_src_))

                raise self.UnknownKeyError("Unknown key: " + key_src) from caught_exception

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

        s1 = self._FIRST_CAP_RE.sub(r'\1_\2', name)
        s1 = s1.replace("__", "_")
        return self._ALL_CAP_RE.sub(r'\1_\2', s1).lower()

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
        :param custom_types:
        :return:
        """
        if type(obj_src) in [str, int, bool, type(None)]:
            return obj_src

        if isinstance(obj_src, dict):
            ret = {}
            for key, value in obj_src.items():
                if type(key) not in [int, str]:
                    raise Exception
                ret[key] = AwsObject.convert_to_dict_static(value, custom_types=custom_types)
            return ret

        if isinstance(obj_src, list):
            return [AwsObject.convert_to_dict_static(value, custom_types=custom_types) for value in obj_src]

        if isinstance(obj_src, AwsObject):
            return obj_src.convert_to_dict()

        if isinstance(obj_src, datetime.datetime):
            return obj_src.strftime("%Y-%m-%d %H:%M:%S.%f%z")

        if isinstance(obj_src, Enum):
            return obj_src.value

        # In most cases it will become str
        # Ugly but efficient
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
