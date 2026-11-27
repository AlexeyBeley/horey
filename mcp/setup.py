"""
horey.mcp setup
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from setuptools import setup, find_namespace_packages
from horey.mcp import __version__

with open("README.md", encoding="utf-8") as file_handler:
    readme_file = file_handler.read()

setup(
    name="horey.mcp",
    version=__version__,
    description="Horey MCP server exposing the tools of the installed horey packages",
    long_description=readme_file,
    author="Horey",
    author_email="user-horey@horey.com",
    license="DWTFYWTPL",
    packages=find_namespace_packages(
        include=["horey.mcp", "horey.mcp.*"]
    ),
    include_package_data=True,
    zip_safe=False,
)
