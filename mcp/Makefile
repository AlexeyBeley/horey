SHELL := /bin/bash

CUR_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CUR_DIR}/..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

PROJECT_BUILD_DIR := ${BUILD_TMP_DIR}/mcp

# Horey packages whose MCP tools are exposed, e.g. make run HOREY_MCP_PACKAGES="jenkins_api github_api"
HOREY_MCP_PACKAGES ?=
MCP_IMAGE := horey-mcp
MCP_CONTAINER_NAME := horey-mcp
MCP_PORT ?= 8090
# Packages' configuration files: <package_name>_configuration.py|json
MCP_CONFIGURATIONS_DIR_PATH ?= /opt/horey/mcp/configurations/


prepare_build_dir:
	rm -rf ${PROJECT_BUILD_DIR} &&\
	mkdir -p ${PROJECT_BUILD_DIR}
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --copy_horey_dependencies --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py --dst_dir_path ${PROJECT_BUILD_DIR} --package_name mcp

build:
	cd .. &&\
	docker build -f mcp/docker/Dockerfile -t ${MCP_IMAGE} --build-arg HOREY_MCP_PACKAGES="${HOREY_MCP_PACKAGES}" .

# AWS credentials passed through from the calling shell; the ones not set there stay unset in the container.
MCP_AWS_ENV_VARS := AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_REGION AWS_DEFAULT_REGION

# Published on 127.0.0.1 only: the server has no authentication.
run: build
	mkdir -p ${MCP_CONFIGURATIONS_DIR_PATH} &&\
	docker rm -f ${MCP_CONTAINER_NAME} 2>/dev/null || true &&\
	docker run -d --name ${MCP_CONTAINER_NAME} \
		-p 127.0.0.1:${MCP_PORT}:8080 \
		-v ${MCP_CONFIGURATIONS_DIR_PATH}:/opt/horey/mcp/configurations:ro \
		$(foreach var,${MCP_AWS_ENV_VARS},-e ${var}) \
		${MCP_IMAGE}

stop:
	docker rm -f ${MCP_CONTAINER_NAME}

logs:
	docker logs -f ${MCP_CONTAINER_NAME}

# Register the server with Claude Code (user scope)
claude_add:
	claude mcp add --scope user --transport http horey http://localhost:${MCP_PORT}/mcp

# Run locally, without docker
run_local:
	source ${VENV_DIR}/bin/activate &&\
	HOREY_MCP_PORT=${MCP_PORT} HOREY_MCP_CONFIGURATIONS_DIR_PATH=${MCP_CONFIGURATIONS_DIR_PATH} HOREY_MCP_PACKAGES="${HOREY_MCP_PACKAGES}" \
	python -m horey.mcp.mcp_server
