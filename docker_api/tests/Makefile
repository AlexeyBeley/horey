SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/../..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_BIN_DIR := $(realpath ${BUILD_TMP_DIR}/_venv/bin)
USERNAME := $(shell whoami)

echo:
	echo ${USERNAME}

build:
	source ${VENV_BIN_DIR}/activate &&\
	cd ${HOREY_DIR_PATH} &&\
	make raw_install_wheel-docker_api

test: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest ${CURRENT_DIR}/ -v

wip_%: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/$(subst wip_,,$@) -v -s

pytest_%: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest --full-trace ${CURRENT_DIR}/$(subst pytest_,,$@) -v -s

# for Mac
wip: FORCE build
	source ${VENV_BIN_DIR}/activate &&\
	DOCKER_HOST=unix:///Users/${USERNAME}/.docker/run/docker.sock python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/ -v -s

FORCE: ;
