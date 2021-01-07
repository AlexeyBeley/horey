
SHELL := /bin/bash

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR= ${ROOT_DIR}/build
BUILD_TMP_DIR= ${BUILD_DIR}/_build
VENV_DIR= ${BUILD_TMP_DIR}/_venv

REQUIREMENTS=~/private/IP

ALL_PACKAGES := $(wildcard *)

EXCLUSIONS := LICENSE Makefile README.md build dns_map docker terraform security_group_map pypi_infra h_flow network
SRC_FILES := $(filter-out $(EXCLUSIONS), $(ALL_PACKAGES))

init_venv_dir:
	mkdir -p ${BUILD_TMP_DIR}
	python3 -m venv ${VENV_DIR} && \
	pip3 install wheel

prepare_package_wheel-%: init_venv_dir
	cp -r ${ROOT_DIR}/$(subst prepare_package_wheel-,,$@) ${BUILD_TMP_DIR} \
	cd ${BUILD_TMP_DIR}/ 
	rm -rf $$VARIABLE\dist; \
	python3 setup.py sdist bdist_wheel; \


install_common_utils: prepare_package_wheel-common_utils
	cd ${BUILD_TMP_DIR} && \


install-%: init_venv_dir install_common_utils
	cd ${BUILD_TMP_DIR} && \
	python3 generate_local_requirements

package_source_requirements: init_venv_dir
	for VARIABLE in ${REQUIREMENTS}; do \
	cd $$VARIABLE; \
	rm -rf $$VARIABLE\dist; \
	python3 setup.py sdist bdist_wheel; \
	done
source_requirements: package_source_requirements
	source ${VENV_DIR}/bin/activate && \
	for VARIABLE in ${REQUIREMENTS}; do \
	cd $$VARIABLE; \
	pip3 install dist/*.whl; \
	done

invoke: install_source_requirements
	source ${VENV_DIR}/bin/activate &&\
	python3 invoke_me.py

raw_invoke:
	source ${VENV_DIR}/bin/activate &&\
	python3 invoke_me.py


pylint: init_venv_dir pylint_raw

raw_pylint:
	source ${VENV_DIR}/bin/activate &&\
	pylint ${ROOT_DIR}/aws_api/src/aws_api.py

clear:
	rm -rf ${BUILD_TMP_DIR}/*

