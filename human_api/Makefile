SHELL := /bin/bash

CUR_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CUR_DIR}/..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

file_path = ${CUR_DIR}/tests/my_input.hapi
#file_path = ${CUR_DIR}/tests/my_incorrect_input.hapi

build:
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_from_source-human_api

validate: build validate_raw

validate_raw:
	source ${VENV_DIR}/bin/activate &&\
	cd ${HOREY_DIR_PATH}/human_api/horey/human_api &&\
	python3 human_api_actor.py --action=validate --file_path=${file_path}