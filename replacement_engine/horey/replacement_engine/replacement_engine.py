import os
import pdb

from horey.h_logger import get_logger

logger = get_logger()


class ReplacementEngine:
    def __init__(self):
        pass

    def perform_recursive_replacements(
        self, replacements_base_dir_path, string_replacements
    ):
        if not os.path.exists(replacements_base_dir_path):
            raise RuntimeError(f"No such directory '{replacements_base_dir_path}'")

        for root, _, filenames in os.walk(replacements_base_dir_path):
            for filename in filenames:
                if filename.startswith("template_"):
                    self.perform_file_string_replacements(
                        root, filename, string_replacements
                    )

    @staticmethod
    def perform_file_string_replacements(root, filename, string_replacements):
        logger.info(
            f"Performing replacements on template dir: '{root}' name: '{filename}'"
        )
        with open(os.path.join(root, filename)) as file_handler:
            file_contents = file_handler.read()

        try:
            new_file_contents = ReplacementEngine.perform_raw_string_replacements(
                file_contents, string_replacements
            )
        except ReplacementEngine.UnresolvedReplacementsError as exception_instance:
            raise ReplacementEngine.UnresolvedReplacementsError(
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

        with open(os.path.join(root, new_filename), "w+") as file_handler:
            file_handler.write(new_file_contents)

    @staticmethod
    def perform_raw_string_replacements(str_src, string_replacements):
        for key in sorted(
            string_replacements.keys(),
            key=lambda key_string: len(key_string),
            reverse=True,
        ):
            if not key.startswith("STRING_REPLACEMENT_"):
                raise ValueError("Key must start with STRING_REPLACEMENT_")
            logger.info(f"Performing replacement in template: key: {key}")
            value = string_replacements[key]
            str_src = str_src.replace(key, value)
        if "STRING_REPLACEMENT_" in str_src:
            raise ReplacementEngine.UnresolvedReplacementsError(
                f"Not all STRING_REPLACEMENT_ were replaced in {str_src}"
            )

        return str_src

    @staticmethod
    def perform_comment_line_replacement(
        file_path, comment_line, replacement_string, keep_comment=False
    ):
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

    @staticmethod
    def check_file_contains(dst_file_path, replacement_string):
        with open(dst_file_path) as file_handler:
            file_contents = file_handler.read()

        return replacement_string in file_contents

    class UnresolvedReplacementsError(ValueError):
        pass
