import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from horey.common_utils import __version__
from setuptools import setup


with open("README.md") as file_handler:
	readme_file = file_handler.read()


setup(
	name="horey.common_utils",
	version=__version__,
	description="Horey common utils package",
	long_description=readme_file,
	author="Horey",
	author_email="alexey.beley@gmail.com",
	license="DWTFYWTPL",
	packages=["horey.common_utils"],
	include_package_data=True,
	zip_safe=False)
