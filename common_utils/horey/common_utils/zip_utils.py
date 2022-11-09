"""
Common utils to work with zipfile

"""

import os
import shutil
import zipfile


class ZipUtils:
    """
    Main class.

    """

    @staticmethod
    def make_archive(zip_file_name, root_dir):
        """
        Make a zip from pythons' global site packages.

        @param zip_file_name:
        @param root_dir:
        @return:
        """

        if zip_file_name.endswith(".zip"):
            zip_file_name = zip_file_name[:-4]

        shutil.make_archive(zip_file_name, 'zip', root_dir=root_dir)

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
                myzip.write(file_path, arcname=os.path.basename(file_path))

    @staticmethod
    def add_dirs_to_zip(zip_file_name, dir_paths):
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

            ZipUtils.add_dir_to_zip(zip_file_name, dir_path)

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
