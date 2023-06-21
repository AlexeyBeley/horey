from horey.h_logger import get_logger
from pprint import pprint

logger = get_logger()


class KubernetesObject:
    SELF_CACHED_TYPE_KEY_NAME = "horey_cached_type"

    def __init__(self, obj_src):
        self.obj_src = obj_src
        self._name = None
        self.metadata = None
        self.spec = None

    @staticmethod
    def pprint(dict_src):
        pprint(dict_src)

    @property
    def name(self):
        if self._name is None:
            self._name = self.metadata["name"]
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

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

    def init_attrs(self, dict_src, dict_options, raise_on_no_option=True):
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
