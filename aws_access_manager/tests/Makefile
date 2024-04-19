SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_BIN_DIR := $(realpath ${BUILD_TMP_DIR}/_venv/bin)



build:
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --install horey.aws_access_manager --force_reinstall --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py


build_aws_api:
	source ${VENV_BIN_DIR}/activate &&\
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_from_source-aws_api


test: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python -m pytest ${CURRENT_DIR}/ -v

wip_%: FORCE build wip_raw_%

wip_raw_%:
	source ${VENV_BIN_DIR}/activate &&\
	python -m pytest -m wip --full-trace ${CURRENT_DIR}/$(subst wip_raw_,,$@) -v -s

wip: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python -m pytest -m wip --full-trace ${CURRENT_DIR}/ -v -s

FORCE: ;
