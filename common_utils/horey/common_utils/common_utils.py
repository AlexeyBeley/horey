"""
Some reusable stuff.

"""

import datetime
import importlib
import os
import sys
import re
from enum import Enum
from horey.common_utils.bash_executor import BashExecutor


class CommonUtils:
    """
    Some stuff to be reused
    """
    SELF_CACHED_TYPE_KEY_NAME = "horey_cached_type"
    _FIRST_CAP_RE = None
    _ALL_CAP_RE = None

    @staticmethod
    def convert_to_dict(obj_src, custom_types=None):
        """
        Converts all known attribute types to a specific form available to be init from cache.

        :param obj_src:
        :param custom_types: list of dicts: {type:converter_function}
        :return:
        """

        # pylint: disable=too-many-branches,too-many-return-statements
        if type(obj_src) in [str, int, bool, type(None), float]:
            return obj_src

        if isinstance(obj_src, dict):
            ret = {}
            for key, value in obj_src.items():
                if type(key) not in [int, str]:
                    raise ValueError(type(key))
                ret[key] = CommonUtils.convert_to_dict(
                    value, custom_types=custom_types
                )
            return ret

        if isinstance(obj_src, list):
            return [
                CommonUtils.convert_to_dict(value, custom_types=custom_types)
                for value in obj_src
            ]

        if isinstance(obj_src, datetime.datetime):
            return {
                CommonUtils.SELF_CACHED_TYPE_KEY_NAME: "datetime",
                "value": obj_src.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            }

        if isinstance(obj_src, Enum):
            return obj_src.value

        if hasattr(obj_src, "convert_to_dict"):
            return obj_src.convert_to_dict()

        if not custom_types:
            # return str(obj_src)
            raise ValueError(f"Unknown type: obj_src {type(obj_src)}")

        if type(obj_src) not in custom_types:
            return str(obj_src)

        return custom_types[type(obj_src)](obj_src)

    @staticmethod
    def init_from_dict(obj_dst, dict_src, custom_types=None):
        """
        Init object from dict

        :param custom_types:
        :param obj_dst:
        :param dict_src:
        :return:
        """

        for key_src, value in dict_src.items():
            if custom_types and key_src in custom_types:
                setattr(obj_dst, key_src, custom_types[key_src](value))
            elif (
                isinstance(value, dict)
                and value.get(CommonUtils.SELF_CACHED_TYPE_KEY_NAME) is not None
            ):
                setattr(obj_dst, key_src, CommonUtils.init_horey_cached_type(value))
            else:
                setattr(obj_dst, key_src, value)

    @staticmethod
    def init_from_api_dict(obj_dst, dict_src, custom_types=None, validate_attributes=True):
        """
        Init object from dict

        :param custom_types:
        :param obj_dst:
        :param dict_src:
        :param validate_attributes:
        :return:
        """

        obj_dst.dict_src = dict_src
        known_attributes = list(obj_dst.__dict__.keys())

        for bound_method in dir(obj_dst):
            if f"_{bound_method}" in known_attributes:
                known_attributes.append(bound_method)

        unknown_attributes = []
        for key_src, value in dict_src.items():
            attribute_new_name = CommonUtils.camel_case_to_snake_case(key_src)
            if attribute_new_name not in known_attributes:
                unknown_attributes.append(attribute_new_name)

            if custom_types and key_src in custom_types:
                setattr(obj_dst, attribute_new_name, custom_types[key_src](value))
            else:
                setattr(obj_dst, attribute_new_name, value)

        if unknown_attributes:
            composed_errors = [f"self.{CommonUtils.camel_case_to_snake_case(key_src)} = None" for key_src in unknown_attributes]
            print("\n".join(composed_errors))
            if validate_attributes:
                raise ValueError(unknown_attributes)

    @staticmethod
    def init_horey_cached_type(value):
        """
        Init automatically cached values

        @param value: {self.SELF_CACHED_TYPE_KEY_NAME: datetime/region/ip..., "value": value_to_init}
        @return:
        """

        if value.get(CommonUtils.SELF_CACHED_TYPE_KEY_NAME) == "datetime":
            # Example: datetime.datetime.strptime('2017-07-26 15:54:10.000000+0000', '%Y-%m-%d %H:%M:%S.%f%z')
            value_formatted = value["value"] if "+" in value["value"] else value["value"] + "+0000"
            return datetime.datetime.strptime(
                value_formatted, "%Y-%m-%d %H:%M:%S.%f%z"
            )
        raise ValueError(f"Unknown horey type: {value}")

    @staticmethod
    def camel_case_to_snake_case(name):
        """
        Camel case to snake case

        @param name:
        @return:
        """

        if CommonUtils._FIRST_CAP_RE is None:
            CommonUtils._FIRST_CAP_RE = re.compile("(.)([A-Z][a-z]+)")
            CommonUtils._ALL_CAP_RE = re.compile("([a-z0-9])([A-Z])")

        s1 = CommonUtils._FIRST_CAP_RE.sub(r"\1_\2", name)
        s1 = s1.replace("__", "_")
        return CommonUtils._ALL_CAP_RE.sub(r"\1_\2", s1).lower()

    @staticmethod
    def find_objects_by_values(objects, values, max_count=None):
        """
        Find objects with all specified values.
        If no such attr: do not add to the return list

        :param objects: list of objects
        :param values: dict of key - value
        :param max_count: Maximum amount to return
        :return:
        """

        objects_ret = []
        for obj in objects:
            for key, value in values.items():
                try:
                    if getattr(obj, key) != value:
                        break
                except AttributeError:
                    break
            else:
                objects_ret.append(obj)
                if max_count is not None and len(objects_ret) >= max_count:
                    break

        return objects_ret

    @staticmethod
    def int_to_str(number):
        """
        Int to comma separated string
        :param number:
        :return:
        """
        if not isinstance(number, int):
            raise ValueError(number)

        # pylint: disable= consider-using-f-string
        str_ret = "{:,}".format(number)

        return str_ret

    @staticmethod
    def bytes_to_str(number):
        """
        Pretty print of storage
        :param number:
        :return:
        """
        if not isinstance(number, int):
            raise ValueError(number)

        if number < 0:
            raise ValueError(number)

        if number == 0:
            return "0"

        mapping = {
            1: "Bytes",
            1024: "KiB",
            1024**2: "MiB",
            1024**3: "GiB",
            1024**4: "TiB",
            1024**5: "PiB",
        }

        key_limit = 1

        for key_limit_tmp, _ in mapping.items():
            if number < key_limit_tmp:
                break
            key_limit = key_limit_tmp
        quotient, remainder = divmod(number, key_limit)
        int_percent_reminder = round((remainder / key_limit) * 100)
        if int_percent_reminder == 0:
            return_number = str(quotient)
        else:
            float_result = float(f"{quotient}.{int_percent_reminder}")
            return_number = str(round(float_result, 2))
        return f"{return_number} {mapping[key_limit]}"

    @staticmethod
    def timestamp_to_datetime(timestamp, microseconds_value=False):
        """
        int/str to datetime.

        @param timestamp:
        @param microseconds_value: Is the value in microseconds
        :return:
        """

        if microseconds_value:
            try:
                timestamp /= 1000
            except TypeError:
                timestamp = int(timestamp) / 1000

        return datetime.datetime.fromtimestamp(timestamp, datetime.UTC)

    @staticmethod
    def load_object_from_module(module_full_path, callback_function_name):
        """
        Load object from python module and runs it as function
        For example 'main()'

        @param module_full_path:
        @param callback_function_name:
        @return:
        """

        return CommonUtils.load_object_from_module_raw(module_full_path, callback_function_name)()

    @staticmethod
    def load_object_from_module_raw(module_full_path, callback_function_name):
        """
        Load object from python module using call_back initiation function.
        For example 'class Main'

        @param module_full_path:
        @param callback_function_name:
        @return:
        """

        module = CommonUtils.load_module(module_full_path)
        return getattr(module, callback_function_name)

    @staticmethod
    def load_module(module_full_path):
        """
        Dynamically load python module.

        @param module_full_path:
        @return:
        """

        module_path = os.path.dirname(module_full_path)
        sys.path.insert(0, module_path)
        module_name = os.path.splitext(os.path.basename(module_full_path))[0]
        module = importlib.import_module(module_name)
        module = importlib.reload(module)

        popped_path = sys.path.pop(0)
        if popped_path != module_path:
            raise RuntimeError(
                f"System Path must not be changed while importing configuration_policy: {module_full_path}. "
                f"Changed from {module_path} to {popped_path}"
            )

        return module

    @staticmethod
    def generate_ed25519_key(owner_email, output_file_path):
        """
        Generate key using bash and ssh-keygen

        :param owner_email:
        :param output_file_path:
        :return:
        """

        command = f'ssh-keygen -t ed25519 -C "{owner_email}" -f {output_file_path} -q -N ""'
        BashExecutor.run_bash(command)
