import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.jenkins_manager import __version__
from setuptools import setup, find_namespace_packages


with open("README.md") as file_handler:
    readme_file = file_handler.read()


setup(
    name="horey.jenkins_manager",
    version=__version__,
    description="Horey jenkins_manager package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(
        include=["horey.jenkins_manager", "horey.jenkins_manager.*"]
    ),
    include_package_data=True,
    zip_safe=False,
)
