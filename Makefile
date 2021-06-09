SHELL := /bin/bash

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR= ${ROOT_DIR}/build
BUILD_TMP_DIR= ${BUILD_DIR}/_build
VENV_DIR= ${BUILD_TMP_DIR}/_venv

ALL_PACKAGES := $(wildcard *)

EXCLUSIONS := LICENSE Makefile README.md build dns_map docker terraform security_group_map pypi_infra h_flow network
SRC_FILES := $(filter-out $(EXCLUSIONS), $(ALL_PACKAGES))

create_build_env:
	mkdir -p ${BUILD_TMP_DIR} &&\
	pip3 install wheel &&\
	pip3 install -U setuptools

init_venv_dir: create_build_env
	python3 -m venv ${VENV_DIR}

prepare_package_wheel-%: init_venv_dir
	${BUILD_DIR}/create_wheel.sh $(subst prepare_package_wheel-,,$@)

recursive_install_from_source_local_venv-%: init_venv_dir
	source ${VENV_DIR}/bin/activate &&\
	pip3 install -U setuptools &&\
	${BUILD_DIR}/recursive_install_from_source.sh --root_dir ${ROOT_DIR} --package_name horey.$(subst recursive_install_from_source_local_venv-,,$@)

package_source-%:
	${BUILD_DIR}/create_wheel.sh $(subst package_source-,,$@)
install_from_source-%: package_source-% init_venv_dir
	source ${VENV_DIR}/bin/activate &&\
	pip3 install --force-reinstall ${BUILD_TMP_DIR}/$(subst install_from_source-,,$@)/dist/*.whl

recursive_install_from_source-%: create_build_env
	${BUILD_DIR}/recursive_install_from_source.sh --root_dir ${ROOT_DIR} --package_name horey.$(subst recursive_install_from_source-,,$@)

install_pylint:
	source ${VENV_DIR}/bin/activate &&\
	pip3 install pylint

pylint: init_venv_dir install_pylint raw_pylint
raw_pylint:
	source ${VENV_DIR}/bin/activate &&\
	pylint  --rcfile=${BUILD_DIR}/.pylintrc ${ROOT_DIR}/aws_api/horey/aws_api/aws_api.py

install_test_deps-%: init_venv_dir
	source ${VENV_DIR}/bin/activate &&\
	pip3 install -r ${ROOT_DIR}/$(subst install_test_deps-,,$@)/tests/requirements.txt

test-configuration_policy: recursive_install_from_source_local_venv-configuration_policy install_test_deps-configuration_policy raw_test-configuration_policy

test-%: recursive_install_from_source_local_venv-% install_test_deps-% raw_test-%
raw_test-%:
	source ${VENV_DIR}/bin/activate &&\
	pytest ${ROOT_DIR}/$(subst raw_test-,,$@)/tests/*.py -s

clean:
	rm -rf ${BUILD_TMP_DIR}/*

#test_azure_api: recursive_install_from_source_local_venv-azure_api
test_azure_api: install_from_source-azure_api
	source ${VENV_DIR}/bin/activate &&\
	cd ${ROOT_DIR}/azure_api/tests &&\
	python3 test_azure_api_init_and_cache.py

#test_azure_api: recursive_install_from_source_local_venv-azure_api
test_aws_api: install_from_source-aws_api
	source ${VENV_DIR}/bin/activate &&\
	cd ${ROOT_DIR}/aws_api/tests &&\
	python3 test_aws_api_init_and_cache.py

install_azure_api_prerequisites:
	source ${VENV_DIR}/bin/activate &&\
	sudo pip3 install --upgrade pip