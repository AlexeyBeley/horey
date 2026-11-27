SHELL := /bin/bash

CUR_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CUR_DIR}/..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

PROJECT_BUILD_DIR := ${BUILD_TMP_DIR}/fb_api


prepare_build_dir:
	rm -rf ${PROJECT_BUILD_DIR} &&\
	mkdir -p ${PROJECT_BUILD_DIR} &&\
	cp ${HOREY_DIR_PATH}/facebook_api/build/Dockerfile ${PROJECT_BUILD_DIR}/Dockerfile
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --copy_horey_dependencies --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py --dst_dir_path ${PROJECT_BUILD_DIR} --package_name facebook_api


.PHONY: build

build: prepare_build_dir
	cd ${PROJECT_BUILD_DIR} &&\
	docker build -t free_stuff_api .
