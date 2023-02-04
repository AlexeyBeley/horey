"""
Serverless packer - used to pack lambdas.

"""
import os
import shutil
import zipfile

from horey.h_logger import get_logger
from horey.pip_api.pip_api import PipAPI
from horey.pip_api.pip_api_configuration_policy import PipAPIConfigurationPolicy
from horey.common_utils.bash_executor import BashExecutor

logger = get_logger()


class Packer:
    """
    Serverless packer - used to pack the lambdas.

    """

    def __init__(self, python_version="3.8"):
        supported_versions = ["3.8", "3.9"]
        if python_version not in supported_versions:
            raise ValueError(f"python_versions supported: {supported_versions}. Received: '{python_version}'")

        self.python_version = python_version
        self.bash_executor = BashExecutor()

    def create_lambda_package(self, lambda_name, deployment_path, package_setup_path):
        """
        Warning For maximum reliability, use a fully-qualified path for the executable.
        To search for an unqualified name on PATH, use shutil.which(). On all platforms,
        passing sys.executable is the recommended way to launch the current Python interpreter again,
        and use the -m command-line format to launch an installed module.
        Resolving the path of executable (or the first item of args) is platform dependent.
        For POSIX, see os.execvpe(), and note that when resolving or searching for the executable path,
        cwd overrides the current working directory and env can override the PATH environment variable.
        For Windows, see the documentation of the lpApplicationName and lpCommandLine parameters of WinAPI
        CreateProcess, and note that when resolving or searching for the executable path with shell=False, cwd does
        not override the current working directory and env cannot override the PATH environment variable.
        Using a full path avoids all of these variations.

        @param package_setup_path:
        @param lambda_name:
        @param deployment_path:
        @return:
        """

        venv_path = os.path.join(deployment_path, "_venv")
        self.create_venv(venv_path)
        self.install_requirements(package_setup_path, venv_path)
        self.zip_venv_site_packages(lambda_name, deployment_path)

    def create_venv(self, venv_path, clean_install=True):
        """
        Trivial

        @param venv_path:
        @param clean_install:
        @return:
        """
        if clean_install:
            if os.path.exists(venv_path):
                logger.info(f"Removing directory {venv_path}")
                shutil.rmtree(venv_path)
        os.makedirs(venv_path, exist_ok=True)

        logger.info(f"Created venv dir: {venv_path}")

        bash_cmd = f"python{self.python_version} -m venv {venv_path}"
        self.execute(bash_cmd)
        self.execute_in_venv("pip3 install --upgrade pip", venv_path)

    def install_requirements(self, package_setup_path, venv_path):
        """
        Simple requirements.txt file installation.

        @param package_setup_path:
        @param venv_path:
        @return:
        """

        command = f"pip3 install -r {package_setup_path}/requirements.txt"
        return self.execute_in_venv(command, venv_path)

    @staticmethod
    def install_horey_requirements(requirements_file_path, venv_path, horey_repo_path):
        """
        Recursive install horey packages from source.

        @param requirements_file_path:
        @param venv_path:
        @param horey_repo_path:
        @return:
        """

        if not os.path.isfile(requirements_file_path):
            raise RuntimeError(
                f"Requirements file does not exist: {requirements_file_path}"
            )

        configuration = PipAPIConfigurationPolicy()
        configuration.multi_package_repositories = [horey_repo_path]
        configuration.venv_dir_path = venv_path
        pip_api = PipAPI(configuration=configuration)
        pip_api.install_requirements(requirements_file_path)

    def uninstall_packages(self, venv_path, packages):
        """
        Uninstall python package. Used by cleanups.

        @param venv_path:
        @param packages:
        @return:
        """
        for package_name in packages:
            logger.info(f"Uninstalling package: {package_name} in venv: {venv_path}")
            command = f"pip3 uninstall {package_name}"
            self.execute_in_venv(command, venv_path)

    def execute_in_venv(self, command, venv_path):
        """
        Execute bash command under venv activate.

        @param command:
        @param venv_path:
        @return:
        """

        logger.info(f"Executing {command} in venv")
        script_content = "!#/bin/bash\n"
        script_content += "set -xe\n"
        script_content += f"source {venv_path}/bin/activate\n"
        script_content += f"{command}\n"

        with open("./tmp_script_to_execute", "w", encoding="utf-8") as fh:
            fh.write(script_content)
        bash_cmd = ["/bin/bash", "./tmp_script_to_execute"]
        return self.execute(bash_cmd)

    @staticmethod
    def get_site_packages_directory(venv_dir_path, python_version):
        """
        Find the direcotry holding the site packages in the venv.

        @param venv_dir_path:
        @param python_version:
        @return:
        """

        return os.path.join(venv_dir_path, "lib", python_version, "site-packages")

    def zip_venv_site_packages(self, zip_file_name, venv_dir_path):
        """
        Make a zip from pythons' global site packages.

        @param zip_file_name:
        @param venv_dir_path:
        @return:
        """

        if zip_file_name.endswith(".zip"):
            zip_file_name = zip_file_name[:-4]

        package_dir = self.get_site_packages_directory(venv_dir_path, f"python_{self.python_version}")
        shutil.make_archive(zip_file_name, "zip", root_dir=package_dir)

    @staticmethod
    def add_files_to_zip(zip_file_name, files_paths):
        """
        Add multiple files to the zip file by their names.

        @param zip_file_name:
        @param files_paths:
        @return:
        """

        with zipfile.ZipFile(zip_file_name, "a") as myzip:
            for file_path in files_paths:
                logger.info(f"Adding file to zip: {file_path}")
                myzip.write(file_path, arcname=os.path.basename(file_path))

    def add_dirs_to_zip(self, zip_file_name, dir_paths):
        """
        Add existing directories to the package.

        @param zip_file_name:
        @param dir_paths:
        @return:
        """

        for dir_path in dir_paths:
            if not os.path.exists(dir_path):
                raise RuntimeError(f"{dir_path} does not exist")

            if not os.path.isdir(dir_path):
                raise RuntimeError(f"{dir_path} is not a dir")

            self.add_dir_to_zip(zip_file_name, dir_path)

    @staticmethod
    def add_dir_to_zip(zip_file_name, dir_path: str):
        """
        Add directory to the zip file.

        @param zip_file_name:
        @param dir_path:
        @return:
        """

        dir_path = dir_path[:-1] if dir_path.endswith("/") else dir_path
        prefix_len = dir_path.rfind("/") + 1
        with zipfile.ZipFile(zip_file_name, "a") as myzip:
            for base_path, _, files in os.walk(dir_path):
                for file_name in files:
                    file_path = os.path.join(base_path, file_name)
                    arc_name = file_path[prefix_len:]
                    myzip.write(file_path, arcname=arc_name)

    @staticmethod
    def extract(zip_file_name, dir_path):
        """
        Extract from zip file

        @param zip_file_name:
        @param dir_path:
        @return:
        """
        with zipfile.ZipFile(zip_file_name) as myzip:
            myzip.extractall(path=dir_path)

    @staticmethod
    def execute(bash_cmd):
        """
        Execute bash command

        @param bash_cmd:
        @return:
        """
        if not isinstance(bash_cmd, str):
            bash_cmd = " ".join(bash_cmd)

        bash_executor = BashExecutor()
        dict_ret = bash_executor.run_bash(bash_cmd, logger=logger)
        return dict_ret["stdout"]

    def copy_venv_site_packages_to_dir(
        self, dst_dir_path, venv_dir_path
    ):
        """
        Copy installed venv packages to the folder to be used for lambda creation.

        @param dst_dir_path:
        @param venv_dir_path:
        @return:
        """

        packages_dir = self.get_site_packages_directory(venv_dir_path, f"python_{self.python_version}")
        for package_dir_name in os.listdir(packages_dir):
            src_package_dir_path = os.path.join(packages_dir, package_dir_name)
            dst_package_dir_path = os.path.join(dst_dir_path, package_dir_name)

            if os.path.isfile(src_package_dir_path):
                if os.path.exists(dst_package_dir_path):
                    os.remove(dst_package_dir_path)
                shutil.copyfile(src_package_dir_path, dst_package_dir_path)
                continue

            if os.path.exists(dst_package_dir_path):
                shutil.rmtree(dst_package_dir_path)
            shutil.copytree(src_package_dir_path, dst_package_dir_path)

    def zip_prepared_directory(self, zip_file_name, src_dir_path):
        """
        Create a zip from prepared directory.

        @param zip_file_name:
        @param src_dir_path:
        @return:
        """

        for file_name in os.listdir(src_dir_path):
            full_path = os.path.join(src_dir_path, file_name)
            if os.path.isdir(full_path):
                self.add_dir_to_zip(zip_file_name, full_path)
            else:
                self.add_files_to_zip(zip_file_name, [full_path])
