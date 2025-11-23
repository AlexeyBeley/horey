SHELL := /bin/bash
PYTHON := $(shell which python >> /dev/null && echo "python" || echo "python3")

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR= ${ROOT_DIR}/build
BUILD_TMP_DIR= ${BUILD_DIR}/_build
VENV_DIR= ${BUILD_TMP_DIR}/_venv

PYLINT_TARGET := "none"

ALL_PACKAGES := $(wildcard *)

EXCLUSIONS := LICENSE Makefile README.md build dns_map docker terraform security_group_map pypi_infra h_flow network
SRC_FILES := $(filter-out $(EXCLUSIONS), $(ALL_PACKAGES))

#apt install python.10-venv -y
#curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#python get-pip.py
#rm get-pip.py
#/usr/bin/python -m pip install -U setuptools>=54.1.2
install-pip:
	sudo apt-get update
	sudo apt-get -y install python3-pip
	python -m pip install --upgrade pip

create_build_env:
	mkdir -p ${BUILD_TMP_DIR} &&\
	python -m pip install wheel &&\
	python -m pip install -U setuptools\>=54.1.2 &&\
	python -m pip install -U packaging\>=24.2

init_venv_dir: create_build_env
	python -m venv ${VENV_DIR} &&\
	source ${VENV_DIR}/bin/activate &&\
	python -m pip install --upgrade pip &&\
	python -m pip install -U setuptools\>=54.1.2 &&\
	python -m pip install -U packaging\>=24.2

install_wheel-%: init_venv_dir raw_install_wheel-%
	echo "done installing $(subst install_wheel-,,$@)"

raw_install_wheel-%: package_source-%
	${PYTHON} -m pip install --force-reinstall ${BUILD_TMP_DIR}/$(subst raw_install_wheel-,,$@)/dist/*.whl

recursive_install_from_source_local_venv-%: init_venv_dir
	source ${VENV_DIR}/bin/activate &&\
	${BUILD_DIR}/recursive_install_from_source.sh --root_dir ${ROOT_DIR} --package_name horey.$(subst recursive_install_from_source_local_venv-,,$@)


package_source-%:
	${BUILD_DIR}/create_wheel.sh $(subst package_source-,,$@)


install_from_source-%: init_venv_dir raw_install_from_source-%

raw_install_from_source-%: package_source-%
	source ${VENV_DIR}/bin/activate &&\
	python -m pip install --force-reinstall ${BUILD_TMP_DIR}/$(subst raw_install_from_source-,,$@)/dist/*.whl


recursive_install_from_source-%: create_build_env
	${BUILD_DIR}/recursive_install_from_source.sh --root_dir ${ROOT_DIR} --package_name horey.$(subst recursive_install_from_source-,,$@)

install_pylint: init_venv_dir
	source ${VENV_DIR}/bin/activate &&\
	python -m pip install pylint

pylint: install_pylint pylint_raw
pylint_raw:
	source ${VENV_DIR}/bin/activate &&\
	pylint --rcfile=${BUILD_DIR}/.pylintrc ${PYLINT_TARGET}

install_test_deps-%: init_venv_dir
	source ${VENV_DIR}/bin/activate &&\
	python -m pip install -r ${ROOT_DIR}/$(subst install_test_deps-,,$@)/tests/requirements.txt


test-%: recursive_install_from_source_local_venv-% install_test_deps-% raw_test-%
raw_test-%:
	source ${VENV_DIR}/bin/activate &&\
	pytest ${ROOT_DIR}/$(subst raw_test-,,$@)/tests/*.py -s

clean:
	rm -rf ${BUILD_TMP_DIR}/*


deploy_client_hooks:
	cp ${BUILD_DIR}/pre-commit ${ROOT_DIR}/.git/hooks/pre-commit

install_black: init_venv_dir
	source ${VENV_DIR}/bin/activate &&\
	python -m pip install black

black: install_black black_raw
black_raw:
	source ${VENV_DIR}/bin/activate &&\
	black ${ROOT_DIR}