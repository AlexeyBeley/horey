import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.alert_system import __version__
from setuptools import setup, find_namespace_packages

with open("README.md") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.alert_system",
    version=__version__,
    description="Horey alert_system package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    include_package_data=True,
    package_data={"": ["lambda_package/*.txt"]},
    packages=find_namespace_packages(
        include=["horey.alert_system",
                 "horey.alert_system.*",
                 "horey.alert_system.lambda_package",
                 "horey.alert_system.lambda_package.*",
                 "horey.alert_system.lambda_package.**.*",
                 ]
    ),
    zip_safe=False,
    install_requires=[],
)
