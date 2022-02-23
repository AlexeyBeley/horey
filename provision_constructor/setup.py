import os
import pdb

import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.provision_constructor import __version__
from setuptools import setup, find_namespace_packages

with open("README.md") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.provision_constructor",
    version=__version__,
    description="Horey provision_constructor package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(include=["horey.provision_constructor", "horey.provision_constructor.*",
                                              "horey.provision_constructor.system_functions",
                                              "horey.provision_constructor.system_functions.*"]),
    package_data={
        "": ["system_functions/**/*.sh",
             "system_functions/**/*.txt",
             "system_functions/**/**/*.conf",
             "system_functions/**/**/*.yml",
             "system_functions/*.txt"
             ],
    },
    include_package_data=True,
    zip_safe=False)
