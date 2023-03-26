"""
horey.azure_devops_api setup
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from setuptools import setup, find_namespace_packages
from horey.azure_devops_api import __version__

with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.azure_devops_api",
    version=__version__,
    description="Horey azure_devops_api package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(
        include=["horey.azure_devops_api", "horey.azure_devops_api.*"]
    ),
    include_package_data=True,
    zip_safe=False,
)
