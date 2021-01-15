import argparse
import sys
import os
import pdb


class Package:
    PROJECT_PACKAGES = {}

    def __init__(self, root_dir, package_name, version_restriction=None):
        if package_name in Package.PROJECT_PACKAGES:
            raise NotImplementedError(f"Circular dependency not yet implemented: {package_name}")
        else:
            Package.PROJECT_PACKAGES[package_name] = self

        self.version_restriction = version_restriction
        self.name = package_name
        self.root_dir = root_dir
        self.dependencies = []

        if self.name.startswith("horey"):
            self._init_horey_dependencies()

    def init_requirement_line(self):
        line = self.name
        if self.version_restriction is not None:
            line += str(self.version_restriction)
        return line

    def __str__(self):
        ret = self.init_requirement_line()
        for dependency in self.dependencies:
            ret += "\n" + str(dependency)
        return ret

    def _init_horey_dependencies(self):
        try:
            requirements_file_path = os.path.join(self.root_dir, self.name[len("horey."):], "requirements.txt")
            with open(requirements_file_path) as file_handler:
                lines = [line.strip() for line in file_handler.readlines()]
        except FileNotFoundError as exception_received:
            print(f"{repr(exception_received)}: {requirements_file_path}")
            return

        for line in lines:
            if line == "":
                continue
            dependency_name, dependency_restriction, version = self._split_dependency_line(line)
            version_restriction = Package.VersionRestriction()
            version_restriction.add_restriction(dependency_restriction, version)
            dependency_package = Package(self.root_dir, dependency_name, version_restriction=version_restriction)
            self.dependencies.append(dependency_package)

    def order_requirements(self):
        lines = []
        for dependency in self.dependencies:
            requirements_lines = dependency.order_requirements()
            lines += requirements_lines

        lines.append(self.init_requirement_line())
        return lines

    @staticmethod
    def _split_dependency_line(line):
        """

        :param line:
        :return: dependency_name, dependency_restriction, version
        """

        if line.find(">") == -1 and line.find("<") == -1 and line.find("=") == -1:
            return line, None, None

        restriction_index = min([i for i in [line.find(">"), line.find("<"), line.find("=")] if i > -1])
        dependency_name = line[:restriction_index]
        i = restriction_index
        while i < len(line):
            if line[i] not in ["<", ">", "="]:
                break
            i += 1
        else:
            raise ValueError(line)

        dependency_restriction = line[restriction_index:i]
        version = line[i:]
        return dependency_name, dependency_restriction, version

    class VersionRestriction:
        def __init__(self):
            self.lower_limit = None
            self.contains_lower_limit = None
            self.upper_limit = None
            self.contains_upper_limit = None

        def __str__(self):
            if self.lower_limit is None and self.upper_limit is None:
                return ""

            if self.lower_limit == self.upper_limit:
                return f"=={self.lower_limit}"

            ret = ""
            if self.lower_limit is not None:
                ret += ">"
                if self.contains_lower_limit is not None:
                    ret += "="
                ret += self.lower_limit

            if self.upper_limit is not None:
                ret += ", <" if ret else "<"

                if self.contains_upper_limit is not None:
                    ret += "="

                ret += self.upper_limit

            return ret

        def add_restriction(self, restriction_key, restriction_value):
            if restriction_key is None:
                if restriction_value is not None:
                    raise ValueError()
                return

            if restriction_value is None:
                if restriction_key is not None:
                    raise ValueError()
                return

            if self.lower_limit is not None:
                raise NotImplementedError(f"{restriction_key}, {restriction_value}")
            if self.contains_lower_limit is not None:
                raise NotImplementedError(f"{restriction_key}, {restriction_value}")
            if self.upper_limit is not None:
                raise NotImplementedError(f"{restriction_key}, {restriction_value}")
            if self.contains_upper_limit is not None:
                raise NotImplementedError(f"{restriction_key}, {restriction_value}")

            if ">" in restriction_key:
                self.lower_limit = restriction_value
                if "=" in restriction_key:
                    self.contains_lower_limit = True
                return

            if "<" in restriction_key:
                self.upper_limit = restriction_value
                if "=" in restriction_key:
                    self.contains_upper_limit = True
                return
            if restriction_key == "==":
                self.lower_limit = restriction_value
                self.contains_lower_limit = True
                self.upper_limit = restriction_value
                self.contains_upper_limit = True
                return

            raise ValueError(restriction_key)


if __name__ == "__main__":
    description = "Compose project's requirements"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--root_dir", required=True, type=str, help="Domain name")
    parser.add_argument("--package_name", required=True, type=str, help="Domain name")
    parser.add_argument("--output_file", required=True, type=str, help="Key to use")
    arguments = parser.parse_args()
    packages_tree = Package(arguments.root_dir, arguments.package_name)

    with open(arguments.output_file, "w+") as file_handler:
        file_handler.write("\n".join(packages_tree.order_requirements()))
