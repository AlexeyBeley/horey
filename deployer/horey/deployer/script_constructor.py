import pdb
import os
import stat
from shutil import copyfile


class ScriptConstructor:
    IMPORTS_SECTION_SEPARATOR = "#_______________imports_section_end__________\n"
    MAIN_SECTION_SEPARATOR = "#_______________main_section_end__________\n"

    def __init__(self, script_file_path):
        self.script_file_path = script_file_path
        self.init_script_file()

    def init_script_file(self):
        if not os.path.exists(self.script_file_path):
            with open(self.script_file_path, "w") as file_handler:
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "data",
                                       "template_bash_script_file.sh")) as template_file_handler:
                    template_script_lines = template_file_handler.readlines()

                    if template_script_lines.count(self.IMPORTS_SECTION_SEPARATOR) != 1:
                        raise RuntimeError(f"Expecting single separator line got {template_script_lines.count(self.IMPORTS_SECTION_SEPARATOR)}: {self.IMPORTS_SECTION_SEPARATOR}")
                    if template_script_lines.count(self.MAIN_SECTION_SEPARATOR) != 1:
                        raise RuntimeError(f"Expecting single separator line got {template_script_lines.count(self.MAIN_SECTION_SEPARATOR)}: {self.MAIN_SECTION_SEPARATOR}")

                    file_handler.writelines(template_script_lines)

        st = os.stat(self.script_file_path)
        os.chmod(self.script_file_path, st.st_mode | stat.S_IEXEC)

    def add_module(self, module_script_path, put_near_script_file=False):
        if put_near_script_file:
            module_script_path = self.put_module_script_file_near_script_file(module_script_path)

        scripts_common_path = os.path.commonpath([self.script_file_path, module_script_path])
        relative_script_file_path_from_common = self.script_file_path[len(scripts_common_path)+1:]
        relative_module_script_path_from_common = module_script_path[len(scripts_common_path) + 1:]
        script_file_to_module_script_relative_path = os.path.join(*([".."] *
                                                                    relative_script_file_path_from_common.count("/") +
                                                                    [relative_module_script_path_from_common]))

        source_line = f"source {script_file_to_module_script_relative_path}"
        self.add_line_to_section(self.IMPORTS_SECTION_SEPARATOR, source_line)

        script_name = os.path.basename(module_script_path)
        function_name = os.path.splitext(script_name)[0]

        with open(module_script_path) as file_handler:
            contents = file_handler.read()

        contents = contents.replace("\n", "")
        while "  " in contents:
            contents = contents.replace("  ", " ")

        if f"function {function_name}() {'{'}" not in contents:
            raise RuntimeError(f"function_name : '{function_name} should present in {module_script_path}'")

        self.add_line_to_section(self.MAIN_SECTION_SEPARATOR, function_name)

    def put_module_script_file_near_script_file(self, module_script_path):
        module_script_filename = os.path.basename(module_script_path)
        new_module_script_file_path = os.path.join(os.path.dirname(self.script_file_path), module_script_filename)
        copyfile(module_script_path, new_module_script_file_path)
        return new_module_script_file_path

    def add_line_to_section(self, separator, line):
        with open(self.script_file_path, "r") as file_handler:
            lines = file_handler.readlines()

        if lines.count(separator) != 1:
            raise RuntimeError(f"Malformed file, expected single separator but got {lines.count(separator)}: '{separator}'")

        line = line if line.endswith("\n") else line + "\n"

        if line in lines:
            return

        lines.insert(lines.index(separator), line)

        with open(self.script_file_path, "w") as file_handler:
            file_handler.writelines(lines)
