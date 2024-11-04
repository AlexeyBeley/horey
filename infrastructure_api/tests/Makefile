SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_BIN_DIR := $(realpath ${BUILD_TMP_DIR}/_venv/bin)


echo:
	echo ${VENV_BIN_DIR}/activate

build_ng:
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --install horey.environment_api --force_reinstall --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py



wip: FORCE build_ng
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/ -v -s



FORCE: ;
