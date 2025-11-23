SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_BIN_DIR := $(realpath ${BUILD_TMP_DIR}/_venv/bin)

# PYTHON_EXECUTABLE := $(which python >> /dev/null && echo "python" || echo "python3")
PYTHON := $(shell which python >> /dev/null && echo "python" || echo "python3")


wip: FORCE
	cd ${HOREY_DIR_PATH} &&\
	make test_wip-pip_api
	# ${PYTHON} -m pytest -m wip --full-trace ${CURRENT_DIR}/ -v -s

FORCE: ;
