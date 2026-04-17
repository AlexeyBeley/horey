"""
from
"""
import os
import sys
from setuptools import setup, find_namespace_packages

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# pylint: disable= wrong-import-order
from horey.questrade_api import __version__

with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.questrade_api",
    version=__version__,
    description="Horey questrade_api package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(
        include=["horey.questrade_api", "horey.questrade_api.*"]
    ),
    include_package_data=True,
    package_data={"": ["questrade_runner/remote_scripts/*.sh"]},
    zip_safe=False,
)
