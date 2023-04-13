SHELL := /bin/bash

TESTS_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${TESTS_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

bla:
	echo ${VENV_DIR}

test_%: FORCE build
	echo ${VENV_DIR} &&\
	source ${VENV_DIR}/bin/activate &&\
	python ${TESTS_DIR}/${@}

FORCE: ;

build:
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_from_source-provision_constructor
	#make recursive_install_from_source_local_venv-provision_constructor
