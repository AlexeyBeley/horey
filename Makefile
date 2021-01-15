
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
	${BUILD_DIR}/create_wheel.sh $(subst prepare_package_wheel-,,$@)

install_required_packages-%:
	cd ${BUILD_DIR} &&\
	python3 generate_local_requirements.py --package_dir ${BUILD_TMP_DIR}/$(subst install_required_packages-,,$@) --output_file ${REQUIRED_HOREY_PACKAGES_FILE_NAME}


recursive_install_from_source-%:
	source ${VENV_DIR}/bin/activate &&\
	${BUILD_DIR}/recursive_install_from_source.sh --root_dir ${ROOT_DIR} --package_name horey.$(subst recursive_install_from_source-,,$@)


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

invoke: install_source_requirements raw_invoke
raw_invoke:
	source ${VENV_DIR}/bin/activate &&\
	python3 invoke_me.py


pylint: init_venv_dir pylint_raw
raw_pylint:
	source ${VENV_DIR}/bin/activate &&\
	pylint ${ROOT_DIR}/aws_api/src/aws_api.py

clear:
	rm -rf ${BUILD_TMP_DIR}/*

