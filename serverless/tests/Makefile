SHELL := /bin/bash

TESTS_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${TESTS_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

bla:
	echo ${HOREY_DIR_PATH}
	#source ${VENV_DIR}/bin/activate &&\
	#pip3 freeze

test_%: FORCE build
	source ${VENV_DIR}/bin/activate &&\
	python ${TESTS_DIR}/${@}

FORCE: ;

.PHONY: build
build:
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_from_source-serverless &&\
	make recursive_install_from_source_local_venv-pip_api &&\
	make recursive_install_from_source_local_venv-aws_api

	#make raw_install_from_source-aws_api
