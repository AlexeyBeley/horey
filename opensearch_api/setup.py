"""
Setup package.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# pylint: disable= wrong-import-order
from horey.opensearch_api import __version__
from setuptools import setup, find_namespace_packages

with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.opensearch_api",
    version=__version__,
    description="Horey opensearch_api package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(
        include=["horey.opensearch_api", "horey.opensearch_api.*"]
    ),
    include_package_data=True,
    zip_safe=False,
)
