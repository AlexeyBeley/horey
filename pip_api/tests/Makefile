SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_BIN_DIR := $(realpath ${BUILD_TMP_DIR}/_venv/bin)

PYTHON_EXECUTABLE := $(which python >> /dev/null && echo python || echo "python3")

test:
	echo ${PYTHON_EXECUTABLE}

build:
	source ${VENV_BIN_DIR}/activate &&\
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_wheel-pip_api &&\
	make recursive_install_from_source_local_venv-pip_api

wip: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/ -v -s

FORCE: ;
