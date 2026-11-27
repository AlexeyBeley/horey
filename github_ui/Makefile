SHELL := /bin/bash

CUR_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CUR_DIR}/..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

PROJECT_BUILD_DIR := ${BUILD_TMP_DIR}/github_ui

# AWS CLI profile whose credentials are passed to the container. Not named AWS_PROFILE:
# make would pick up the shell's AWS_PROFILE, while the default profile is what is wanted here.
AWS_CREDENTIALS_PROFILE ?= default


prepare_build_dir:
	rm -rf ${PROJECT_BUILD_DIR} &&\
	mkdir -p ${PROJECT_BUILD_DIR}
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --copy_horey_dependencies --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py --dst_dir_path ${PROJECT_BUILD_DIR} --package_name github_ui

build:
	cd .. &&\
	docker build -f github_ui/docker/Dockerfile -t horey-github-ui .

# Credentials are read from the AWS CLI profile and passed to docker by name (-e NAME), not by value,
# so they do not show up in the process list or in make's output.
# EXPORT_AWS_CREDENTIALS is the first part of a recipe command: it exports the credentials to the environment.
EXPORT_AWS_CREDENTIALS = export AWS_ACCESS_KEY_ID="$$(aws configure get aws_access_key_id --profile ${AWS_CREDENTIALS_PROFILE})" &&\
	export AWS_SECRET_ACCESS_KEY="$$(aws configure get aws_secret_access_key --profile ${AWS_CREDENTIALS_PROFILE})" &&\
	export AWS_SESSION_TOKEN="$$(aws configure get aws_session_token --profile ${AWS_CREDENTIALS_PROFILE} 2>/dev/null || true)" &&\
	if [ -z "$$AWS_ACCESS_KEY_ID" ] || [ -z "$$AWS_SECRET_ACCESS_KEY" ]; then \
		echo "ERROR: no static aws_access_key_id/aws_secret_access_key in AWS profile '${AWS_CREDENTIALS_PROFILE}'" >&2; exit 1; \
	fi &&\
	if [ -z "$$AWS_SESSION_TOKEN" ]; then unset AWS_SESSION_TOKEN; fi

DOCKER_RUN_ENV = --network pgnet \
	-e GITHUB_API_CONFIGURATION_SECRET_NAME="github_api_configuration.json" \
	-e GITHUB_API_CONFIGURATION_SECRET_REGION="ca-central-1" \
	-e POSTGRES_API_CONFIGURATION_SECRET_NAME="postgres_api_configuration.json" \
	-e POSTGRES_API_CONFIGURATION_SECRET_REGION="ca-central-1" \
	-e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN

run: build
	@${EXPORT_AWS_CREDENTIALS} &&\
	docker run --rm -p 8080:8080 ${DOCKER_RUN_ENV} horey-github-ui

# Applies the alembic migrations (alembic/versions) to the database of the Postgres API configuration.
# Runs in the image: the entry point downloads the configurations, then runs the command passed to it.
alembic_migrate: build
	@${EXPORT_AWS_CREDENTIALS} &&\
	docker run --rm ${DOCKER_RUN_ENV} horey-github-ui alembic -c /opt/horey/github_ui/alembic.ini upgrade head


# pgAdmin on http://localhost:${PGADMIN_PORT}, on the same docker network as postgres (pgnet), so the server is reachable by its container name.
# The login password is not stored here: pass it in the environment, e.g.
#   PGADMIN_DEFAULT_PASSWORD=... make pgadmin
# pgAdmin data (servers, settings, login) is kept in PGADMIN_DATA_DIR_PATH on the host, so it survives the container.
# The image runs as uid 5050: on Linux the directory must be writable by it (sudo chown -R 5050:5050 <dir>).
PGADMIN_DATA_DIR_PATH ?= /opt/horey/github_ui/pgadmin/
PGADMIN_DEFAULT_EMAIL ?= admin@horey.com
PGADMIN_PORT ?= 5050

pgadmin:
	@if [ -z "$$PGADMIN_DEFAULT_PASSWORD" ]; then \
		echo "ERROR: PGADMIN_DEFAULT_PASSWORD must be set in the environment" >&2; exit 1; \
	fi &&\
	mkdir -p ${PGADMIN_DATA_DIR_PATH} &&\
	docker run --rm --name horey-pgadmin -p ${PGADMIN_PORT}:80 \
	--network pgnet \
	-e PGADMIN_DEFAULT_EMAIL="${PGADMIN_DEFAULT_EMAIL}" \
	-e PGADMIN_DEFAULT_PASSWORD \
	-v ${PGADMIN_DATA_DIR_PATH}:/var/lib/pgadmin \
	dpage/pgadmin4
