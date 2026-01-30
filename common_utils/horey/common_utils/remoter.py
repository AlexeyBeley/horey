"""
SSH, SFTP etc.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any, Tuple


class Remoter(ABC):
    """
    Remote work manager
    """

    def get_state(self) -> dict:
        """
        Get the remote server state

        :return:
        """

    @abstractmethod
    def get_deployment_dir(self) -> Path:
        """
        Get deployment directory.

        :return:
        """

    @abstractmethod
    def execute(self, command: str, *output_validators: List[Any]) -> Tuple[List[str], List[str], int]:
        """
        Execute remote.

        :return: lst stdout, lst stderr, int error-code
        """

    @abstractmethod
    def put_file(self, src: Path, dst: Path, sudo: bool = False):
        """
        Put local file remotely

        :param src:
        :param dst:
        :param sudo:
        :return:
        """

    @abstractmethod
    def put_directory(self, src: Path, dst: Path, sudo: bool = False):
        """
        Put local directory remotely

        :param src:
        :param dst:
        :param sudo:
        :return:
        """


    @abstractmethod
    def get_file(self, src: Path, dst: Path, sudo: bool = False):
        """
        Get remote file to local disk.

        :param src:
        :param dst:
        :param sudo:
        :return:
        """
