SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

FORCE: ;

build_ng:
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --install horey.free_stuff_api --force_reinstall --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py


wip: FORCE build_ng
	source ${VENV_DIR}/bin/activate &&\
	python -m pytest -m wip ${CURRENT_DIR}/ -v -s

test:
	echo ${HOREY_DIR_PATH}/free_stuff_api

prepare_build_test:
	mkdir -p ${HOREY_DIR_PATH}/build_test

build_docker: prepare_build_test
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --copy_horey_dependencies --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py --dst_dir_path ${HOREY_DIR_PATH}/build_test --package_name free_stuff_api &&\
	cp -f ${HOREY_DIR_PATH}/free_stuff_api/build/DockerfileARM ${HOREY_DIR_PATH}/build_test/Dockerfile &&\
	cp -rf ${HOREY_DIR_PATH}/pip_api ${HOREY_DIR_PATH}/build_test/horey &&\
	docker build -t test -f ${HOREY_DIR_PATH}/build_test/Dockerfile ${HOREY_DIR_PATH}/build_test


dwip: FORCE build_docker
	docker run -it test