# python setup.py build_ext --inplace
from setuptools import setup, Extension
from pathlib import Path

module = Extension('example', 
include_dirs=[Path(__file__).parent],
sources=[
        "wrapper.c",
    ],
    extra_link_args=["-Wl,-undefined,dynamic_lookup"],  # Required for macOS)
)

setup(name='ExampleExtension',
      version='1.0',
      description='Python extension module for calling Go code',
      ext_modules=[module])