import os
import pdb

import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.replacement_engine import __version__
from setuptools import setup, find_namespace_packages

with open("README.md") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.replacement_engine",
    version=__version__,
    description="Horey replacement_engine package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(include=["horey.replacement_engine", "horey.replacement_engine.*"]),
    package_data={
        "": ["replacement_engine/**/*.sh"
             ],
    },
    include_package_data=True,
    zip_safe=False)
