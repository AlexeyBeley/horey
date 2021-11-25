import pdb
import subprocess
import os
import shutil
import zipfile

from horey.h_logger import get_logger

logger = get_logger()


class Packer:
    def __init__(self):
        pass

    def create_lambda_package(self, lambda_name, deployment_path, package_setup_path):
        """
        Warning For maximum reliability, use a fully-qualified path for the executable. To search for an unqualified name on PATH, use shutil.which(). On all platforms, passing sys.executable is the recommended way to launch the current Python interpreter again, and use the -m command-line format to launch an installed module.
        Resolving the path of executable (or the first item of args) is platform dependent. For POSIX, see os.execvpe(), and note that when resolving or searching for the executable path, cwd overrides the current working directory and env can override the PATH environment variable. For Windows, see the documentation of the lpApplicationName and lpCommandLine parameters of WinAPI CreateProcess, and note that when resolving or searching for the executable path with shell=False, cwd does not override the current working directory and env cannot override the PATH environment variable. Using a full path avoids all of these variations.
        @param package_setup_path:
        @param lambda_name:
        @param deployment_path:
        @return:
        """

        """
        python3.8 -m venv ${VENV_DIR}
        source ${VENV_DIR}/bin/activate &&\
        pip3 install --upgrade pip &&\
        pip3 install -U setuptools
        
        @param deployment_path:
        @return: 
        """

        venv_path = os.path.join(deployment_path, "_venv")
        self.create_venv(venv_path)
        self.install_requirements(package_setup_path, venv_path)
        self.zip_venv_site_packages(lambda_name, deployment_path)

    def create_venv(self, venv_path, clean_install=True):
        if clean_install:
            if os.path.exists(venv_path):
                logger.info(f"Removing directory {venv_path}")
                shutil.rmtree(venv_path)
        os.makedirs(venv_path, exist_ok=True)

        logger.info(f"Created venv dir: {venv_path}")

        bash_cmd = f"python3.8 -m venv {venv_path}"
        self.execute(bash_cmd)
        self.execute_in_venv("pip3 install --upgrade pip", venv_path)

    def install_requirements(self, package_setup_path, venv_path):
        command = f"pip3 install -r {package_setup_path}/requirements.txt"
        return self.execute_in_venv(command, venv_path)

    def execute_in_venv(self, command, venv_path):
        logger.info(f"Executing {command} in venv")
        script_content = f"!#/bin/bash\n"
        script_content += f"set -xe\n"
        script_content += f"source {venv_path}/bin/activate\n"
        script_content += f"{command}\n"

        with open("./tmp", "w") as fh:
            fh.write(script_content)
        bash_cmd = ["/bin/bash", "./tmp"]
        return self.execute(bash_cmd)

    def zip_venv_site_packages(self, zip_file_name, venv_dir_path, python_version):
        package_dir = os.path.join(venv_dir_path, "lib", python_version, "site-packages")
        shutil.make_archive(zip_file_name, 'zip', root_dir=package_dir)

    def add_files_to_zip(self, zip_file_name, files_paths):
        with zipfile.ZipFile(zip_file_name, "a") as myzip:
            for file_path in files_paths:
                myzip.write(file_path, arcname=os.path.basename(file_path))

    def pip_freeze(self):
        "pip3 freeze --all"

    def execute(self, bash_cmd, shell=False):
        if isinstance(bash_cmd, str):
            bash_cmd = bash_cmd.split(" ")

        process = subprocess.run(bash_cmd, capture_output=True, text=True, shell=shell)
        if process.returncode != 0:
            raise RuntimeError(f"{process.stdout}\n{process.stderr}")
        return process

    def create_lambda_package_from_python_package(self):
        raise NotImplementedError()
        import sys
        sys.argv = ["--help"]

        import unittest
        from unittest.mock import Mock
        import pdb

        setup_mock = Mock()
        with unittest.mock.patch("setuptools.setup", setup_mock):
            from setup import setup
            ret = setup_mock.call_args

            # function_name = setup_mock.call_args["main"]

            ret.kwargs["name"]
            ret.kwargs["python_requires"]
            ret.kwargs["packages"]

        pdb.set_trace()
