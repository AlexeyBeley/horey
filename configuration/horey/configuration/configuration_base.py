import pdb
import os
import logging
import json
import yaml


handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel("INFO")
logger.addHandler(handler)


class Configuration:
    """
    1) No methods. Configuration is a static data - you can set or get values.
    2) Configuration context is immutable - once you set context rules, ancestors can not change the rules.
    3) Every value being set must be defined in a property.
    * Property can be defined only at one level of inheritance.
    * Set attribute with name "attribute_name" only when self has "_attribute_name" attribute.
    """

    ENVIRON_ATTRIBUTE_PREFIX = "horey_"

    def __init__(self):
        pass

    def _set_attribute_value(self, attribute_name, attribute_value):
        if not hasattr(self, f"_{attribute_name}"):
            raise ValueError(attribute_name)

        setattr(self, attribute_name, attribute_value)

    def init_from_command_line(self, parser):
        namespace_arguments = parser.parse_args()
        dict_arguments = vars(namespace_arguments)
        self.init_from_dictionary(dict_arguments, custom_source_log="Init attribute '{}' from command line argument")

    def init_from_dictionary(self, dict_src, custom_source_log=None):
        """
        Because everything is a dict we will path custom log line to indicate what is the real source of the value.

        :param dict_src:
        :param custom_source_log:
        :return:
        """
        for key, value in dict_src.items():
            if custom_source_log is not None:
                log_line = custom_source_log.format(key)
            else:
                log_line = f"Init attribute '{key}' from dictionary"

            logger.info(log_line)
            self._set_attribute_value(key, value)

    def init_from_environ(self):
        for key_tmp, value in os.environ.items():
            key = key_tmp.lower()
            if key.startswith(self.ENVIRON_ATTRIBUTE_PREFIX):
                key = key[len(self.ENVIRON_ATTRIBUTE_PREFIX):]

                log_line = f"Init attribute '{key}' from environment variable '{key_tmp}'"
                logger.info(log_line)

                self._set_attribute_value(key, value)

    def init_from_json_file(self, file_path):
        with open(file_path) as file_handler:
            dict_arguments = json.load(file_handler)
        self.init_from_dictionary(dict_arguments, custom_source_log="Init attribute '{}' from json file: '" + file_path + "'")

    def init_from_yaml_file(self, file_path):
        with open(file_path) as file_handler:
            dict_arguments = yaml.load(file_handler)
        self.init_from_dictionary(dict_arguments, custom_source_log="Init attribute '{}' from yaml file: '" + file_path + "'")
