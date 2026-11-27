"""
horey.github_ui setup
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from setuptools import setup, find_namespace_packages
from horey.github_ui import __version__

with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.github_ui",
    version=__version__,
    description="Horey github_ui package",
    long_description=readme_file,
    author="Horey",
    author_email="user-horey@horey.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(
        include=["horey.github_ui", "horey.github_ui.*"]
    ),
    include_package_data=True,
    package_data={
        "": ["html/*.html"]
    },
    zip_safe=False,
)
