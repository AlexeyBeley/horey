"""
Package creator

"""

import os

import sys
# pylint:disable = wrong-import-order
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.health_api import __version__
from setuptools import setup, find_namespace_packages

with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.health_api",
    version=__version__,
    description="Horey health_api package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(include=["horey.health_api", "horey.health_api.*"]),
    package_data={
        "": ["health_api/**/*.sh"],
    },
    include_package_data=True,
    zip_safe=False,
)
