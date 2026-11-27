"""
Git API config.

"""

from horey.configuration_policy.configuration_policy import ConfigurationPolicy


# pylint: disable = missing-function-docstring
class GitAPIConfigurationPolicy(ConfigurationPolicy):
    """
    Main class

    """

    def __init__(self):
        super().__init__()
        self._remote_address = None
        self._remote_name = None
        self._ssh_key_file_path = None
        self._directory_path = None
        self._git_directory_path = None
        self._main_branch = None
        self._main_branch_name = None
        self._pat = None
        self._user = None
        self._repository_name = None
        self._organisation_name = None

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def pat(self):
        return self._pat

    @pat.setter
    def pat(self, value):
        self._pat = value

    @property
    def main_branch_name(self):
        if self._main_branch_name is None:
            return "main"
        return self._main_branch_name

    @main_branch_name.setter
    def main_branch_name(self, value):
        self._main_branch_name = value

    @property
    def main_branch(self):
        return self._main_branch

    @main_branch.setter
    def main_branch(self, value):
        self._main_branch = value

    @property
    def git_directory_path(self):
        self.check_defined()
        return self._git_directory_path

    @git_directory_path.setter
    @ConfigurationPolicy.directory_property(mkdir=True, exist_ok=True)
    def git_directory_path(self, value):
        self._git_directory_path = value

    @property
    def directory_path(self):
        if self._directory_path is None:
            remote = self.remote_address[:-len(".git")] if self.remote_address.endswith(".git") else self.remote_address
            dir_name = remote.split("/")[-1]
            if not dir_name or any(symbol in dir_name for symbol in [".", " "]):
                raise RuntimeError(f"Invalid: '{dir_name=}' generated from remote: {self.remote_address}")
            self._directory_path = self.git_directory_path / dir_name

        return self._directory_path

    @directory_path.setter
    @ConfigurationPolicy.directory_property(mkdir=True, exist_ok=True)
    def directory_path(self, value):
        self._directory_path = value

    @property
    def remote_address(self):
        self.check_defined()
        return self._remote_address

    @remote_address.setter
    def remote_address(self, value):
        self._remote_address = value

    @property
    def remote_name(self):
        self.check_defined()
        return self._remote_name

    @remote_name.setter
    def remote_name(self, value):
        self._remote_name = value

    @property
    def organisation_name(self):
        if self._organisation_name is None:
            self._init_repo_and_org_names()

        return self._organisation_name

    def _init_repo_and_org_names(self):
        """
        Init from remote
        """

        if self.remote_address.startswith("https"):
            # https://github.com/AlexeyBeley/horey.git
            self._organisation_name, self._repository_name = self.remote_address.split("/")[3:]
        else:
            # git@github.com:AlexeyBeley/horey.git
            self._organisation_name, self._repository_name = self.remote_address.split(":")[1].split("/")

    @property
    def repository_name(self):
        if self._repository_name is None:
            self._init_repo_and_org_names()
        return self._repository_name


    @property
    def ssh_key_file_path(self):
        return self._ssh_key_file_path

    @ssh_key_file_path.setter
    def ssh_key_file_path(self, value):
        self._ssh_key_file_path = value
