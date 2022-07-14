SHELL := /bin/bash

TESTS_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${TESTS_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

bla:
	echo ${VENV_DIR}

test_%: FORCE build
	source ${VENV_DIR}/bin/activate &&\
	python3 ${TESTS_DIR}/${@}

FORCE: ;

build_:
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_from_source-alert_system

build:
	source ${VENV_DIR}/bin/activate &&\
	cd ${HOREY_DIR_PATH} &&\
	make recursive_install_from_source-alert_system

LAST_DEPLOYMENT_DIR := $(shell ls /tmp/alert_system |tail -1)
ZIP_PATH := "/tmp/alert_system/${LAST_DEPLOYMENT_DIR}/lambda_function.zip"
DIR_PATH := $(shell dirname ${ZIP_PATH})

tst:
	echo ${LAST_DEPLOYMENT_DIR}
run_lambda_locally:
	cd "${DIR_PATH}" &&\
	mkdir -p "${DIR_PATH}/lambda_function" &&\
	tar xf "${ZIP_PATH}" --directory "${DIR_PATH}/lambda_function" &&\
	cp -i "${TESTS_DIR}/venv_tester.py" "${DIR_PATH}/lambda_function" &&\
	cd "${DIR_PATH}/lambda_function" &&\
	python3 venv_tester.py
