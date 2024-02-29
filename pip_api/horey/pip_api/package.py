"""
Installed package.

"""
from requirement import Requirement


class Package:
    """
    Installed package.

    """

    def __init__(self, dict_src):
        self.name = dict_src["name"]
        self.version = dict_src["version"]
        self.multi_package_repo_prefix = None
        self.multi_package_repo_path = None

    def check_version_requirements(self, requirement: Requirement):
        """
        Check req.
        :param requirement:
        :return:
        """
        self_int_version_lst = [int(sub_ver) for sub_ver in self.version.split(".")]

        return self.check_version_min_requirement(
            requirement, self_int_version_lst
        ) and self.check_version_max_requirement(requirement, self_int_version_lst)

    def check_version_min_requirement(self, requirement, self_int_version_lst):
        """
        Check self version against min required version

        :param requirement:
        :param self_int_version_lst:
        :return:
        """

        if requirement.min_version == self.version:
            if requirement.include_min:
                return True
            return False
        if requirement.min_version is None:
            return True

        requirement_int_version_lst = [
            int(sub_ver) for sub_ver in requirement.min_version.split(".")
        ]
        for index, package_sub_ver_value in enumerate(self_int_version_lst):
            try:
                if package_sub_ver_value > requirement_int_version_lst[index]:
                    break
            except IndexError:
                break

            if package_sub_ver_value < requirement_int_version_lst[index]:
                return False

        return True

    def check_version_max_requirement(self, requirement, self_int_version_lst):
        """
        Check max req.

        :param requirement:
        :param self_int_version_lst:
        :return:
        """
        print(self_int_version_lst)
        if requirement.max_version is None:
            return True

        if requirement.max_version == self.version:
            if requirement.include_max:
                return True
            return False

        exception_text = f"todo: requirement.name: {requirement.name}, " \
                         f"self.version: {self.version}, " \
                         f"requirement.max_version: {requirement.max_version}"

        if requirement.requirements_file_path is not None:
            exception_text += f", requirements_file_path: {requirement.requirements_file_path}"

        raise NotImplementedError(exception_text)
