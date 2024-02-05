"""
Packager.

"""

import os
import sys
from setuptools import setup

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.async_orchestrator import __version__


with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()


setup(
    name="horey.async_orchestrator",
    version=__version__,
    description="Horey async orchestrator package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=["horey.async_orchestrator"],
    include_package_data=True,
    zip_safe=False,
)
