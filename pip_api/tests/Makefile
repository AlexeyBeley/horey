SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_BIN_DIR := $(realpath ${BUILD_TMP_DIR}/_venv/bin)


echo:
	echo ${VENV_BIN_DIR}/activate

venv:
	python -m venv ${BUILD_TMP_DIR}/_venv &&\
	source ${VENV_BIN_DIR}/activate &&\
	python -m pip install --upgrade pip &&\
	python -m pip install -U setuptools\>=54.1.2 &&\
	python -m pip install -U packaging\>=24.2 &&\
	python -m pip install pytest &&\
	cd ${HOREY_DIR_PATH} &&\
	make recursive_install_from_source_local_venv-pip_api

build: venv
	source ${VENV_BIN_DIR}/activate &&\
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_wheel-pip_api

test: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest ${CURRENT_DIR}/ -v

wip_%: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/$(subst wip_,,$@) -v -s

pytest_%: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest --full-trace ${CURRENT_DIR}/$(subst pytest_,,$@) -v -s

wip: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/ -v -s

test_pip_api_make: FORCE
	python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/test_pip_api_make.py -v -s



FORCE: ;
