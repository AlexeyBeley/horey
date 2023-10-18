"""
String composition.

"""
import json
import os

from horey.h_logger import get_logger

logger = get_logger()


class ReplacementEngine:
    """
    Main class.

    """

    def __init__(self):
        pass

    def perform_recursive_replacements(
        self, replacements_base_dir_path, string_replacements, cartesian_replacements=None
    ):
        """
        Replacing place holders in a dir.

        :param cartesian_replacements:
        :param replacements_base_dir_path:
        :param string_replacements:
        :return:
        """

        if not os.path.exists(replacements_base_dir_path):
            raise RuntimeError(f"No such directory '{replacements_base_dir_path}'")

        for root, _, filenames in os.walk(replacements_base_dir_path):
            for filename in filenames:
                if filename.startswith("template_"):
                    self.perform_file_string_replacements(
                        root, filename, string_replacements, cartesian_replacements=cartesian_replacements
                    )

    @staticmethod
    def perform_file_string_replacements(root, filename, string_replacements, cartesian_replacements=None):
        """
        Perform file replacements.

        :param cartesian_replacements:
        :param root:
        :param filename:
        :param string_replacements:
        :return:
        """

        logger.info(
            f"Performing replacements on template dir: '{root}' name: '{filename}'"
        )
        with open(os.path.join(root, filename), encoding="utf-8") as file_handler:
            file_contents = file_handler.read()

        try:
            new_file_contents = ReplacementEngine.perform_raw_string_replacements(
                file_contents, string_replacements, validate=cartesian_replacements is None
            )
            if cartesian_replacements:
                new_file_contents = ReplacementEngine.perform_raw_cartesian_replacements(new_file_contents, cartesian_replacements)
        except Exception as exception_instance:
            raise ValueError(
                f"Replacing file contents of {os.path.join(root, filename)}"
            ) from exception_instance

        new_filename = filename[len("template_") :]
        try:
            new_filename = ReplacementEngine.perform_raw_string_replacements(
                new_filename, string_replacements
            )
        except ReplacementEngine.UnresolvedReplacementsError as exception_instance:
            raise ReplacementEngine.UnresolvedReplacementsError(
                f"Replacing file name {os.path.join(root, filename)}"
            ) from exception_instance

        with open(os.path.join(root, new_filename), "w+", encoding="utf-8") as file_handler:
            file_handler.write(new_file_contents)

    @staticmethod
    def perform_raw_string_replacements(str_src, string_replacements, validate=True):
        """
        Replace strings in the file.

        :param validate:
        :param str_src:
        :param string_replacements:
        :return:
        """

        for key in sorted(
            string_replacements.keys(),
            key=len,
            reverse=True,
        ):
            if not key.startswith("STRING_REPLACEMENT_"):
                raise ValueError("Key must start with STRING_REPLACEMENT_")
            logger.info(f"Performing replacement in template: key: {key}")
            value = string_replacements[key]
            str_src = str_src.replace(key, value)

        if validate and "STRING_REPLACEMENT_" in str_src:
            raise ReplacementEngine.UnresolvedReplacementsError(
                f"Not all STRING_REPLACEMENT_ were replaced in {str_src}"
            )

        return str_src

    @staticmethod
    def perform_string_cartesian_replacements(str_src, string_to_list_replacements):
        """
        Perform string cartesian replacements.

        :param str_src:
        :param string_to_list_replacements:
        :return:
        """

        results_aggregator = [str_src]
        for replacement_key in sorted(
                string_to_list_replacements.keys(),
                key=len,
                reverse=True,
        ):
            if not replacement_key.startswith("STRING_REPLACEMENT_"):
                raise ValueError("Key must start with STRING_REPLACEMENT_")

            single_key_results_aggregator = []
            for aggregator_string_source in results_aggregator:
                if replacement_key in aggregator_string_source:
                    if aggregator_string_source.count(replacement_key) > 1:
                        raise NotImplementedError(aggregator_string_source)
                    single_key_results_aggregator += [
                        aggregator_string_source.replace(replacement_key, replacement_value) for
                        replacement_value in string_to_list_replacements[replacement_key]]
                else:
                    single_key_results_aggregator.append(aggregator_string_source)
            results_aggregator = single_key_results_aggregator

        return results_aggregator

    @staticmethod
    def perform_raw_recursive_cartesian_replacements(json_src, string_to_list_replacements):
        """
        Perform replacements on serialized object.

        :param json_src:
        :param string_to_list_replacements:
        :return:
        """

        if isinstance(json_src, str):
            if "STRING_REPLACEMENT_" in json_src:
                raise ReplacementEngine.UnresolvedReplacementsError(
                    f"Not all STRING_REPLACEMENT_ were replaced in {json_src}"
                )
            return json_src

        if json_src is None:
            return None

        if isinstance(json_src, (bool, float, int)):
            return json_src

        if isinstance(json_src, dict):
            return {_key: ReplacementEngine.perform_raw_recursive_cartesian_replacements(_value, string_to_list_replacements) for _key, _value in json_src.items()}

        if isinstance(json_src, list):
            ret = []
            for string_source in json_src:
                if not isinstance(string_source, str):
                    ret.append(ReplacementEngine.perform_raw_recursive_cartesian_replacements(string_source, string_to_list_replacements))
                    continue
                results_aggregator = ReplacementEngine.perform_string_cartesian_replacements(string_source, string_to_list_replacements)

                ret += results_aggregator
            return ret

        raise ValueError(f"Unknown type: {json_src=}, {type(json_src)=}")

    @staticmethod
    def perform_raw_cartesian_replacements(str_src, string_to_list_replacements):
        """
        Replace placeholder strings in the string.

        :param str_src:
        :param string_to_list_replacements:
        :return:
        """

        src_json = json.loads(str_src)
        new_json = ReplacementEngine.perform_raw_recursive_cartesian_replacements(src_json, string_to_list_replacements)
        new_str = json.dumps(new_json, indent=4)

        if "STRING_REPLACEMENT_" in new_str:
            raise ReplacementEngine.UnresolvedReplacementsError(
                f"Not all STRING_REPLACEMENT_ were replaced in {new_str}"
            )

        return new_str

    @staticmethod
    def perform_comment_line_replacement(
        file_path, comment_line, replacement_string, keep_comment=False
    ):
        """
        Find comment line and replace with a string line.

        :param file_path:
        :param comment_line:
        :param replacement_string:
        :param keep_comment:
        :return:
        """
        if not comment_line.endswith("\n"):
            comment_line += "\n"

        with open(file_path, "r", encoding="utf-8") as file_handler:
            lines = file_handler.readlines()

        if keep_comment:
            lines.insert(lines.index(comment_line), replacement_string)
        else:
            lines[lines.index(comment_line)] = replacement_string

        with open(file_path, "w", encoding="utf-8") as file_handler:
            file_handler.writelines(lines)

    @staticmethod
    def check_file_contains(dst_file_path, replacement_string):
        """
        Check if the file contains the string.

        :param dst_file_path:
        :param replacement_string:
        :return:
        """

        with open(dst_file_path, encoding="utf-8") as file_handler:
            file_contents = file_handler.read()

        return replacement_string in file_contents

    class UnresolvedReplacementsError(ValueError):
        """
        There are placeholders which were not replaced.
        """
