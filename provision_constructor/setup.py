"""
Provision constructor - run your system provisioning as code.
"""
import os

import sys
from setuptools import setup, find_namespace_packages

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.provision_constructor import __version__


with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.provision_constructor",
    version=__version__,
    description="Horey provision_constructor package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(
        include=[
            "horey.provision_constructor",
            "horey.provision_constructor.*",
            "horey.provision_constructor.system_functions",
            "horey.provision_constructor.system_functions.*",
        ]
    ),
    package_data={
        "": [
            "bootstrap.sh",
            "bash_tools/*.sh",
            "system_functions/**/*.sh",
            "system_functions/**/*.txt",
            "system_functions/**/*.conf",
            "system_functions/**/**/*.conf",
            "system_functions/**/**/*.yml",
            "system_functions/**/**/*.txt",
            "system_functions/**/**/*.sh",
            "system_functions/*.txt",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
