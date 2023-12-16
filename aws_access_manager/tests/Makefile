SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_BIN_DIR := $(realpath ${BUILD_TMP_DIR}/_venv/bin)



build:
	source ${VENV_BIN_DIR}/activate &&\
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_from_source-aws_api &&\
	make raw_install_from_source-aws_access_manager

build_aws_api:
	source ${VENV_BIN_DIR}/activate &&\
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_from_source-aws_api


test: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python -m pytest ${CURRENT_DIR}/ -v

wip_%: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python -m pytest -m wip --full-trace ${CURRENT_DIR}/$(subst wip_,,$@) -v -s

wip: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python -m pytest -m wip --full-trace ${CURRENT_DIR}/ -v -s

FORCE: ;
