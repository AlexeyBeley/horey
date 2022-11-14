import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.network import __version__
from setuptools import setup


with open("README.md") as file_handler:
    readme_file = file_handler.read()


setup(
    name="horey.network",
    version=__version__,
    description="Horey network package",
    long_description=readme_file,
    author="Horey",
    author_email="alexey.beley@gmail.com",
    license="DWTFYWTPL",
    packages=["horey.network"],
    include_package_data=True,
    zip_safe=False,
)
