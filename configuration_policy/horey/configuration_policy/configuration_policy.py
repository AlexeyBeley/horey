import os
import json
import argparse


from horey.h_logger import get_logger
from horey.common_utils.common_utils import CommonUtils

logger = get_logger()


class ConfigurationPolicy:
    """
    Base class to handle Configuration Policies.
    Should be capt as simple as possible as it should run in various environments.
    ENVIRON_ATTRIBUTE_PREFIX - prefix used to specify which environ values should be used to init configuration.
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

    def _set_attribute_value(
        self, attribute_name, attribute_value, ignore_undefined=False
    ):
        if not hasattr(self, f"_{attribute_name}"):
            if ignore_undefined:
                logger.info(
                    f"{attribute_name} value is not set - no attribute definition"
                )
                return

            raise ValueError(
                f"No attribute found with name _{attribute_name} in {self.__class__.__name__}"
            )

        setattr(self, attribute_name, attribute_value)

    def init_from_command_line(self, parser=None):
        """
        Very important notice: expects all values are strings. Attributes with None value - being removed.
        """

        if parser is None:
            parser = self.generate_parser()
        namespace_arguments = parser.parse_args()
        dict_arguments = vars(namespace_arguments)

        dict_arguments = {
            key: value for key, value in dict_arguments.items() if value is not None
        }

        self.init_from_dictionary(
            dict_arguments,
            custom_source_log="Init attribute '{}' from command line argument",
        )

    def init_from_dictionary(
        self, dict_src, custom_source_log=None, ignore_undefined=False
    ):
        """

        :param dict_src:
        :param custom_source_log: Because everything is a dict we will path custom log line to indicate what is the real source of the value.
        :return:
        """
        for key, value in dict_src.items():
            if custom_source_log is not None:
                log_line = custom_source_log.format(key)
            else:
                log_line = f"Init attribute '{key}' from dictionary"
            logger.info(log_line)
            try:
                self._set_attribute_value(key, value, ignore_undefined=ignore_undefined)
            except self.StaticValueError as error_inst:
                logger.warning(f"Ignoring static value: {error_inst}")

    def init_from_environ(self):
        for key_tmp, value in os.environ.items():
            key = key_tmp.lower()
            if key.startswith(self.ENVIRON_ATTRIBUTE_PREFIX):
                key = key[len(self.ENVIRON_ATTRIBUTE_PREFIX) :]

                log_line = (
                    f"Init attribute '{key}' from environment variable '{key_tmp}'"
                )
                logger.info(log_line)

                self._set_attribute_value(key, value)

    def init_from_file(self):
        if self.configuration_file_full_path is None:
            raise ValueError("Configuration file was not set")

        if self.configuration_file_full_path.endswith(".py"):
            return self.init_from_python_file()

        if self.configuration_file_full_path.endswith(".json"):
            return self.init_from_json_file()

        raise TypeError(f"Known file types: [.py, .json]. Unknown filetype received: {self.configuration_file_full_path}")

    def init_from_python_file(self):
        config = CommonUtils.load_object_from_module(
            self.configuration_file_full_path, "main"
        )
        self.init_from_dictionary(
            config.__dict__,
            custom_source_log="Init attribute '{}' from python file: '"
            + self.configuration_file_full_path
            + "'",
        )

    def init_from_json_file(self):
        with open(self.configuration_file_full_path) as file_handler:
            dict_arguments = json.load(file_handler)
        self.init_from_dictionary(
            dict_arguments,
            custom_source_log="Init attribute '{}' from json file: '"
            + self.configuration_file_full_path
            + "'",
        )

    def generate_parser(self):
        """
        This function generates a parser based on exposed parameters.
        """

        """
        parse_known_args - if Tr
        """
        description = f"{self.__class__.__name__} autogenerated parser"
        parser = argparse.ArgumentParser(description=description)

        for parameter in self.__dict__:
            if not parameter.startswith("_"):
                continue
            parameter = f"--{parameter[1:]}"
            parser.add_argument(parameter, type=str, required=False)

        return parser

    def convert_to_dict(self, ignore_undefined=False):
        dict_ret = {}
        for key in self.__dict__.keys():
            if not key.startswith("_"):
                continue
            attr_name = key[1:]
            try:
                dict_ret[attr_name] = getattr(self, attr_name)
            except self.UndefinedValueError as received_exception:
                if not ignore_undefined:
                    raise ValueError(
                        f"Value can not be accessed for attribute: {attr_name}"
                    ) from received_exception
            except Exception as received_exception:
                raise ValueError(
                    f"Value can not be accessed for attribute: {attr_name}"
                ) from received_exception

        if dict_ret["configuration_file_full_path"] is None:
            del dict_ret["configuration_file_full_path"]

        return dict_ret

    def print(self):
        for key, value in self.convert_to_dict(ignore_undefined=True).items():
            print(f"{key}: {value}")

    def generate_configuration_file(self, output_file_name):
        """
        Generated JSON configuration file from self properties.

        :param output_file_name:
        :return:
        """

        dict_values = self.convert_to_dict()

        with open(output_file_name, "w+") as file_handler:
            json.dump(dict_values, file_handler, indent=4)

    def init_from_policy(self, configuration, ignore_undefined=False):
        self_definable_attrs = [
            attr_name[1:] for attr_name in self.__dict__ if attr_name.startswith("_")
        ]
        for attr_name, value in configuration.convert_to_dict(
            ignore_undefined=ignore_undefined
        ).items():
            if attr_name not in self_definable_attrs:
                logger.info(
                    f"Skipping attribute {attr_name} from {type(configuration)} policy"
                )
                continue
            try:
                log_line = (
                    f"Init attribute '{attr_name}' from {type(configuration)} policy"
                )
                setattr(self, attr_name, value)
                logger.info(log_line)
            except AttributeError:
                if not ignore_undefined:
                    raise
            except ConfigurationPolicy.StaticValueError:
                pass

    @staticmethod
    def validate_type_decorator(types):
        def function_receiver(func):
            def function_wrapper(*args, **kwargs):
                if isinstance(types, list):
                    if type(args[0]) not in types:
                        raise ValueError(
                            f"Received type '{type(args[0])}' while expecting one of '{types}'"
                        )
                else:
                    if isinstance(args[0], types):
                        raise ValueError(
                            f"Received type '{type(args[0])}' while expecting '{types}'"
                        )

                func(*args, **kwargs)

            return function_wrapper

        return function_receiver

    @staticmethod
    def validate_value_is_not_none_decorator(property_getter_function):
        """
        Is being called when @property is called.
        The property_getter_function is this:

        @property
        @validate_value_is_not_none_decorator
        def property_getter_function(configuration_instance)

        @param property_getter_function:
        @return:
        """

        def property_function(configuration_instance):
            _value = getattr(
                configuration_instance, "_" + property_getter_function.__name__
            )
            if _value is None:
                raise ConfigurationPolicy.UndefinedValueError(
                    f"_{property_getter_function.__name__} is None"
                )
            return property_getter_function(configuration_instance)

        return property_function

    class StaticValueError(RuntimeError):
        pass

    class UndefinedValueError(RuntimeError):
        pass
