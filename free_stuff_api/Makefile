SHELL := /bin/bash

CUR_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CUR_DIR}/..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

PROJECT_BUILD_DIR := ${BUILD_TMP_DIR}/fb_api
FRS_CONFIG_FILE_PATH := ${HOREY_DIR_PATH}/../"ignore"/"frs_api_docker_configuration.py"

.PHONY: build_ng

build_ng:
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --install horey.free_stuff_api --force_reinstall --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py


update_component: build_ng
	source ${VENV_DIR}/bin/activate &&\
	python ${HOREY_DIR_PATH}/free_stuff_api/horey/free_stuff_api/free_stuff_api_actor.py --action update_component --free_stuff_api_config_file_path ${FRS_CONFIG_FILE_PATH}
