import os
import pdb

import sys
#sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dependencies import __version__
from setuptools import setup, find_namespace_packages

with open("README.md") as file_handler:
    readme_file = file_handler.read()

setup(
    name="test_lambda_package",
    python_requires="==3.8",
    version=__version__,
    description="Horey serverless package test",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(include=["dependencies", "dependencies.*"]),
    include_package_data=True,
    zip_safe=False)
