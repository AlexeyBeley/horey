"""
SSH, SFTP etc.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any


class StorageService(ABC):
    """
    Remote work manager
    """

    def upload(self, local_path: Path, remote_path: str):
        """
        Upload file

        :param local_path:
        :param remote_path:
        :return:
        """

    def list(self) -> List[str]:
        """
        List all files

        :return:
        """

    def download(self, remote_path: str, local_path: Path):
        """
        Download file

        :param remote_path:
        :param local_path:
        :return:
        """

