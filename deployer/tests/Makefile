SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)
VENV_BIN_DIR := $(realpath ${VENV_DIR}/bin)

bla:
	echo ${VENV_DIR}

test_%: FORCE build
	source ${VENV_DIR}/bin/activate &&\
	python3 ${TESTS_DIR}/${@}

FORCE: ;

build:
	cd ${HOREY_DIR_PATH} &&\
	make recursive_install_from_source_local_venv-deployer
	#make raw_install_from_source-deployer

wip: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python -m pytest -m wip --full-trace ${CURRENT_DIR}/ -v -s
