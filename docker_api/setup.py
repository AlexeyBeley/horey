import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.docker_api import __version__
from setuptools import setup

with open("README.md") as file_handler:
    readme_file = file_handler.read()

setup(name="horey.docker_api",
      version=__version__,
      description="Horey docker_api package",
      long_description=readme_file,
      author="Horey",
      author_email="alexey.beley@gmail.com",
      license="DWTFYWTPL",
      packages=["horey.docker_api"],
      include_package_data=True,
      zip_safe=False)
