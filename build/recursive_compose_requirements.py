"""
Compose multiple packages' requirements into single file
"""

import argparse
import os
from enum import Enum


class Package:
    """
    Python Package

    """
    PROJECT_PACKAGES = {}
    PACKAGE_VERSION_POLICY = 0

    def __init__(self, root_dir, package_name, version_restriction=None):
        self.version_restriction = version_restriction
        self.name = package_name
        self.root_dir = root_dir
        self.dependencies = []

        if package_name in Package.PROJECT_PACKAGES:
            print(f"package_name: {package_name}")
            Package.PROJECT_PACKAGES[package_name].version_restriction = self.select_package_version_restriction(self.version_restriction, Package.PROJECT_PACKAGES[package_name].version_restriction)
        else:
            Package.PROJECT_PACKAGES[package_name] = self
            if self.name.startswith("horey"):
                self._init_horey_dependencies()

    @staticmethod
    def select_package_version_restriction(first, second):
        """
        Select the restriction to be used.
        Happens when 2 packages require the same package.

        @param first:
        @param second:
        @return:
        """

        if str(first) == str(second):
            return first

        if second is None:
            return first

        if first is None:
            return second

        first_lower_limit = "0.0.0" if first.lower_limit is None else first.lower_limit
        second_lower_limit = "0.0.0" if second.lower_limit is None else second.lower_limit
        first_upper_limit = "100000.0.0" if first.lower_limit is None else first.lower_limit
        second_upper_limit = "100000.0.0" if second.lower_limit is None else second.lower_limit

        if Package.PACKAGE_VERSION_POLICY == Package.PackageVersionPolicy.UPGRADE.value:
            restriction = Package.VersionRestriction()
            restriction.lower_limit = max(first_lower_limit, second_lower_limit)
            restriction.contains_lower_limit = first.contains_lower_limit if restriction.lower_limit == first.lower_limit else second.contains_lower_limit

            restriction.upper_limit = max(first_upper_limit, second_upper_limit)
            restriction.contains_upper_limit = first.contains_upper_limit if restriction.upper_limit == first.upper_limit else second.contains_upper_limit
            raise NotImplementedError('min("2.2.3", "10.0.0") = 10.0.0')
        raise NotImplementedError(f"Unknown version restriction {first.lower_limit}")

    def init_requirement_line(self):
        """
        Initiate a line from self to be added to requirements file.

        @return:
        """

        line = self.name
        if self.version_restriction is not None:
            line += str(self.version_restriction)
        return line

    def __str__(self):
        """
        Create string from all dependencies.

        @return:
        """
        ret = self.init_requirement_line()
        for dependency in self.dependencies:
            ret += "\n" + str(dependency)
        return ret

    def _init_horey_dependencies(self):
        """
        Search for "horey." lines. Init packages from them.

        @return:
        """

        requirements_file_path = os.path.join(self.root_dir, self.name[len("horey."):], "requirements.txt")
        try:
            with open(requirements_file_path, encoding="utf-8") as _file_handler:
                lines = [line.strip() for line in _file_handler.readlines()]
        except FileNotFoundError as exception_received:
            print(f"{repr(exception_received)}: {requirements_file_path}")
            return

        for line in lines:
            if line == "":
                continue
            dependency_name, dependency_restriction, version = self.split_dependency_line(line)
            version_restriction = Package.VersionRestriction()
            try:
                version_restriction.add_restriction(dependency_restriction, version)
            except Exception as exception_inst:
                raise RuntimeError(f"In file {requirements_file_path}") from exception_inst

            dependency_package = Package(self.root_dir, dependency_name, version_restriction=version_restriction)
            self.dependencies.append(dependency_package)

    def order_requirements(self):
        """
        Order requirements to be installed in.

        @return:
        """

        lines = []
        for dependency in self.dependencies:
            requirements_lines = dependency.order_requirements()
            lines += requirements_lines

        lines.append(self.init_requirement_line())
        return lines

    @staticmethod
    def split_dependency_line(line):
        """
        Split by math signs.

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
        """
        Restrictions of a package version.
        """
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
        # pylint: disable= too-many-branches
        def add_restriction(self, restriction_key, restriction_value):
            """
            Add another restriction

            @param restriction_key:
            @param restriction_value:
            @return:
            """

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

            raise ValueError(f"{restriction_key}, {restriction_value}")

    class PackageVersionPolicy(Enum):
        """
        How to handle version conflicts.

        """
        UPGRADE = 0
        DOWNGRADE = 1
        RAISE_EXCEPTION = 2


def split(_requirements):
    """
    Split to horey and global.

    @param _requirements:
    @return:
    """

    _horey_req, _global_req = [], []
    for req in _requirements:
        if req.startswith("horey."):
            dependency_name, _, _ = Package.split_dependency_line(req)
            _horey_req.append(dependency_name[len("horey."):])
        else:
            _global_req.append(req)
    return _horey_req, _global_req


if __name__ == "__main__":
    description = "Compose project's requirements"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--root_dir", required=True, type=str, help="Domain name")
    parser.add_argument("--package_name", required=True, type=str, help="Domain name")
    parser.add_argument("--output_horey_file", required=True, type=str, help="Key to use")
    parser.add_argument("--output_requirements_file", required=True, type=str, help="Key to use")
    arguments = parser.parse_args()
    packages_tree = Package(arguments.root_dir, arguments.package_name)

    requirements = packages_tree.order_requirements()
    horey_req, global_req = split(requirements)

    with open(arguments.output_horey_file, "w+", encoding="utf-8") as file_handler:
        file_handler.write("\n".join(horey_req) + "\n")

    with open(arguments.output_requirements_file, "w+", encoding="utf-8") as file_handler:
        file_handler.write("\n".join(global_req) + "\n")
