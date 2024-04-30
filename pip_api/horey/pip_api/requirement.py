"""
Package requirement.

"""


class Requirement:
    """
    Main class.
    """

    def __init__(self, requirements_file_path, requirement_str_src):
        self.requirements_file_path = requirements_file_path
        requirement_str = requirement_str_src.replace(" ", "")

        self.str_src = requirement_str_src
        self.name = None
        self.min_version = None
        self.max_version = None
        self.include_min = None
        self.include_max = None
        self._force = False
        self.multi_package_repo_prefix = None
        self.multi_package_repo_path = None

        if ">" in requirement_str:
            self.name, version = requirement_str.split(">")
            if "=" in version:
                version = version.strip("=")
                self.include_min = True
            else:
                self.include_min = False
            self.min_version = version
            return

        if "<" in requirement_str:
            self.name, version = requirement_str.split("<")
            if "=" in version:
                version = version.strip("=")
                self.include_max = True
            else:
                self.include_max = False
            self.max_version = version
            return

        if "==" in requirement_str:
            self.name, version = requirement_str.split("==")
            self.min_version = version
            self.max_version = version
            self.include_min = True
            self.include_max = True
            return

        self.name = requirement_str

    @property
    def force(self):
        """
        Force reinstall

        :return:
        """
        return self._force

    @force.setter
    def force(self, value):
        """
        Force reinstall setter- can be set on a package level to ensure the package is reinstalled.

        :param value:
        :return:
        """

        if not isinstance(value, bool):
            raise ValueError("force must be bool")
        self._force = value

    def generate_install_string(self):
        """
        Package name + restriction
        eg. horey.test>=1.0.0

        :return:
        """

        ret = self.name
        if self.min_version is not None:
            if self.min_version == self.max_version:
                ret += f"=={self.min_version}"
                return ret
            ret += ">"
            if self.include_min:
                ret += "="
            ret += self.min_version

        if self.max_version:
            ret += "<"
            if self.include_max:
                ret += "="

            ret += self.max_version

        return ret
