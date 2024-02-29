"""
Packager.

"""

import os
import sys
from setuptools import setup

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.lion_king import __version__


with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.lion_king",
    version=__version__,
    description="Horey async orchestrator package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=["horey.lion_king"],
    include_package_data=True,
    package_data={
        "": [os.path.join(os.path.abspath(os.curdir), "horey", "lion_king", "source_code", "*"),
             os.path.join(os.path.abspath(os.curdir), "horey", "lion_king", "grafana", "*"),
             os.path.join(os.path.abspath(os.curdir), "horey", "lion_king", "adminer", "*")
             ]},
    zip_safe=False,
)
