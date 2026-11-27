# horey
My packages. Do whatever you want with them.


## Installing a package:
This will install a package with its requirements.
There are 2 types of requirements: 
* `global` - standard pypi packages installed with pip3.
* `horey.` - recursively installed from source.


### In the global environment
```
make recursive_install_from_source-aws_api
```

### In the venv: `build/_build/_venv`
```
make recursive_install_from_source_local_venv-aws_api
```

## Running pylint:
```shell
make pylint
```

## Run unit tests
```shell
make test
```

## Clean the environment
```shell
make clean
```

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)