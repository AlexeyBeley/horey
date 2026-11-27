SHELL := /bin/bash

CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CURRENT_DIR}/..)
GIT_DIR_PATH := $(realpath ${HOREY_DIR_PATH}/..) 
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR = ${BUILD_DIR}/_build
VENV_BIN_DIR = $(realpath ${BUILD_TMP_DIR}/_venv/bin)

FILE_PATH := $(CURRENT_DIR)/tests/workflows/workflow1.yaml

echo:
	echo ${VENV_BIN_DIR}/activate

build_ng:
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --install horey.github_api --force_reinstall --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py



wip: FORCE build_ng
	source ${VENV_BIN_DIR}/activate &&\
	python3 -m pytest -m wip --full-trace ${CURRENT_DIR}/tests -v -s

get_workflow_dependency_tree: FORCE build_ng
	source ${VENV_BIN_DIR}/activate &&\
	python $(CURRENT_DIR)/horey/github_api/github_api_actor.py --action get_workflow_dependency_tree --workflow_file_path "${FILE_PATH}"

get_workflow_dependency_tree_horey: FORCE build_ng
	source ${VENV_BIN_DIR}/activate &&\
	python $(CURRENT_DIR)/horey/github_api/github_api_actor.py --action get_workflow_dependency_tree --workflow_file_path "${FILE_PATH}" --git_dir_path "${GIT_DIR_PATH}" 

FORCE: ;
