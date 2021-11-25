import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.serverless import __version__
from setuptools import setup, find_namespace_packages

with open("README.md") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.serverless",
    version=__version__,
    description="Horey serverless package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(include=["horey.serverless", "horey.serverless.*"]),
    include_package_data=True,
    zip_safe=False)
