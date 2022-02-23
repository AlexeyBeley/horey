import os
import pdb

from horey.h_logger import get_logger

logger = get_logger()


class ReplacementEngine:
    def __init__(self):
        pass

    def perform_recursive_replacements(self, replacements_base_dir_path, string_replacements):
        if not os.path.exists(replacements_base_dir_path):
            raise RuntimeError(f"No such directory '{replacements_base_dir_path}'")

        for root, _, filenames in os.walk(replacements_base_dir_path):
            for filename in filenames:
                if filename.startswith("template_"):
                    self.perform_file_string_replacements(root, filename, string_replacements)

    @staticmethod
    def perform_file_string_replacements(root, filename, string_replacements):
        logger.info(f"Performing replacements on template dir: '{root}' name: '{filename}'")
        with open(os.path.join(root, filename)) as file_handler:
            str_file = file_handler.read()

        for key in sorted(string_replacements.keys(), key=lambda key_string: len(key_string), reverse=True):
            if not key.startswith("STRING_REPLACEMENT_"):
                raise ValueError("Key must start with STRING_REPLACEMENT_")
            logger.info(f"Performing replacement in template: {filename}, key: {key}")
            value = string_replacements[key]
            str_file = str_file.replace(key, value)

        new_filename = filename[len("template_"):]

        with open(os.path.join(root, new_filename), "w+") as file_handler:
            file_handler.write(str_file)

        if "STRING_REPLACEMENT_" in str_file:
            raise ValueError(f"Not all STRING_REPLACEMENT_ were replaced in {os.path.join(root, new_filename)}")

    @staticmethod
    def perform_comment_line_replacement(file_path, comment_line, replacement_string, keep_comment=False):
        if not comment_line.endswith("\n"):
            comment_line += "\n"

        with open(file_path, "r") as file_handler:
            lines = file_handler.readlines()

        if keep_comment:
            lines.insert(lines.index(comment_line), replacement_string)
        else:
            lines[lines.index(comment_line)] = replacement_string

        with open(file_path, "w") as file_handler:
            file_handler.writelines(lines)

