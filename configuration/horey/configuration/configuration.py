import pdb
import os
import logging
import json
import importlib
import sys
#import yaml

from horey.h_logger import get_logger
logger = get_logger()


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
        """
        Save all the files used to configure - used for prints in
        """
        self._configuration_file_full_path = []
    
    @property
    def configuration_file_full_path(self):
        if len(self._configuration_file_full_path) > 0:
            return self._configuration_file_full_path[-1]
        return None
    
    @configuration_file_full_path.setter
    def configuration_file_full_path(self, value):
        if not os.path.exists(value):
            raise ValueError(f"File does not exist: {value}")

        self._configuration_file_full_path.append(value)

    @property
    def configuration_files_history(self):
        return self._configuration_file_full_path

    @configuration_files_history.setter
    def configuration_files_history(self, _):
        raise ValueError("Readonly property")

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

    def init_from_file(self):
        if self.configuration_file_full_path is None:
            raise ValueError("Configuration file was not set")

        if self.configuration_file_full_path.endswith(".py"):
            return self.init_from_python_file()

    def init_from_python_file(self):
        module_path = os.path.dirname(self.configuration_file_full_path)
        sys.path.insert(0, module_path)
        module_name = os.path.basename(self.configuration_file_full_path).strip(".py")
        module = importlib.import_module(module_name)
        module = importlib.reload(module)
        main_func = getattr(module, "main")
        config = main_func()

        if sys.path.pop(0) != module_path:
            raise RuntimeError(f"System Path must not be changed while importing configuration: {self.configuration_file_full_path}")

        self.init_from_dictionary(config.__dict__, custom_source_log="Init attribute '{}' from python file: '" + self.configuration_file_full_path + "'")

    def init_from_json_file(self, file_path):
        with open(file_path) as file_handler:
            dict_arguments = json.load(file_handler)
        self.init_from_dictionary(dict_arguments, custom_source_log="Init attribute '{}' from json file: '" + file_path + "'")

    def init_from_yaml_file(self, file_path):
        with open(file_path) as file_handler:
            dict_arguments = yaml.load(file_handler)
        self.init_from_dictionary(dict_arguments, custom_source_log="Init attribute '{}' from yaml file: '" + file_path + "'")
