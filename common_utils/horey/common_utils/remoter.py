"""
SSH, SFTP etc.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any


class Remoter(ABC):
    """
    Remote work manager
    """

    @abstractmethod
    def execute(self, command: str, *output_validators: List[Any]) -> (List[str], List[str], int):
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
    def get_file(self, src: Path, dst: Path, sudo: bool = False):
        """
        Get remote file to local disk.

        :param src:
        :param dst:
        :param sudo:
        :return:
        """
