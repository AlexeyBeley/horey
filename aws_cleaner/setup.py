"""
Package creation mechanism.

"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# pylint: disable= wrong-import-order

from horey.aws_cleaner import __version__
from setuptools import setup, find_namespace_packages

with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.aws_cleaner",
    version=__version__,
    description="Horey aws_cleaner package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    include_package_data=True,
    package_data={"": ["aws_cleaner/*.json"]},
    packages=find_namespace_packages(
        include=["horey.aws_cleaner", "horey.aws_cleaner.*"]
    ),
    zip_safe=False,
    install_requires=[],
)
