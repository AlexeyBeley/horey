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
	python3 ${TESTS_DIR}/${@}

FORCE: ;

.PHONY: build
build:
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_from_source-serverless
