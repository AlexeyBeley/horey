SHELL := /bin/bash

CUR_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
HOREY_DIR_PATH := $(realpath ${CUR_DIR}/..)
BUILD_DIR := ${HOREY_DIR_PATH}/build
BUILD_TMP_DIR := ${BUILD_DIR}/_build
VENV_DIR := $(realpath ${BUILD_TMP_DIR}/_venv)

PROJECT_BUILD_DIR := ${BUILD_TMP_DIR}/postgres_api


prepare_build_dir:
	rm -rf ${PROJECT_BUILD_DIR} &&\
	mkdir -p ${PROJECT_BUILD_DIR}
	python ${HOREY_DIR_PATH}/pip_api/horey/pip_api/pip_api_make.py --copy_horey_dependencies --pip_api_configuration ${HOREY_DIR_PATH}/pip_api_configuration.py --dst_dir_path ${PROJECT_BUILD_DIR} --package_name postgres_api

POSTGRES_CONTAINER_NAME := horey-postgres
POSTGRES_IMAGE := postgres:17
POSTGRES_DB := horey
POSTGRES_PASSWORD := SkiT\#%343GDwGH!\#N
POSTGRES_HOST_DATA_DIR := /opt/horey/postgres/

run_postgres_container:
	mkdir -p ${POSTGRES_HOST_DATA_DIR} &&\
	docker run -d \
		--name ${POSTGRES_CONTAINER_NAME} \
		-e POSTGRES_DB=${POSTGRES_DB} \
		-e POSTGRES_PASSWORD='${POSTGRES_PASSWORD}' \
		-v ${POSTGRES_HOST_DATA_DIR}:/var/lib/postgresql/data \
		-p 5432:5432 \
		${POSTGRES_IMAGE}
