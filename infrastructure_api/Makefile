SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := ${CURRENT_DIR}/..
INFRASTRUCTURE_API_DIR := ${CURRENT_DIR}/horey/infrastructure_api
VENV_BIN_DIR := ${CURRENT_DIR}/../build/_build/_venv/bin

FORCE: ;

build_ng:
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --install horey.infrastructure_api --force_reinstall --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py


cleanup: build_ng
	source ${VENV_BIN_DIR}/activate &&\
	python ${INFRASTRUCTURE_API_DIR}/environment_api_actor.py --action cleanup


wip: FORCE build_ng
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/tests -v -s


