SHELL := /bin/bash

ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
CONFIGURATION_FILE_PATH := ${ROOT_DIR}/../../ignore/aws_api_configuration_values.py

AWS_API_DIR := ${ROOT_DIR}/horey/aws_api
AWS_API_CLIENTS_DIR := ${AWS_API_DIR}/aws_clients
VENV_BIN_DIR := ${ROOT_DIR}/../build/_build/_venv/bin

SECRET_NAME := "name"
SECRET_VALUE := "value"


#SECRET_FILE_NAME := "tmp.py"
#SECRET_FILE_PATH := "private/ignore/${SECRET_FILE_NAME}"

SECRET_FILE_NAME := "xxx.pem"
SECRET_FILE_PATH := "/Users/xxx/.ssh/xxx/${SECRET_FILE_NAME}"

test:
	echo ${CONFIGURATION_FILE_PATH}

aws_api_cleanup-%:
	source ${VENV_BIN_DIR}/activate &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action cleanup --target $(subst aws_api_cleanup-,,$@) --configuration_file_full_path ${CONFIGURATION_FILE_PATH}

aws_api_init_and_cache-%:
	source ${VENV_BIN_DIR}/activate &&\
	export PYTHONPATH=${AWS_API_DIR} &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action init_and_cache --target $(subst aws_api_init_and_cache-,,$@) --configuration_file_full_path ${CONFIGURATION_FILE_PATH}

aws_api_sts_set:
	source ${VENV_BIN_DIR}/activate &&\
	python3 ${AWS_API_CLIENTS_DIR}/session_manager_actor.py --action set_session_credentials --profile_name current --configuration_file_full_path ${CONFIGURATION_FILE_PATH}
	#export AWS_PROFILE=current

install_pytest:
	source ${VENV_BIN_DIR}/activate &&\
	pip3 install pytest

test_aws_api_init: install_pytest
	source ${VENV_BIN_DIR}/activate &&\
	pytest ${ROOT_DIR}/tests/test_aws_api_init_and_cache.py

test_aws_api_cleanup: install_pytest
	source ${VENV_BIN_DIR}/activate &&\
	pytest ${ROOT_DIR}/tests/test_aws_api_cleanup.py

put_secret_value:
	source ${VENV_BIN_DIR}/activate &&\
	export PYTHONPATH=${AWS_API_DIR} &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action put_secret_value --secret_name ${SECRET_NAME} --secret_value ${SECRET_VALUE} --configuration_file_full_path ${CONFIGURATION_FILE_PATH}

put_secret_file:
	source ${VENV_BIN_DIR}/activate &&\
	export PYTHONPATH=${AWS_API_DIR} &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action put_secret_file --secret_name ${SECRET_FILE_NAME} --secret_file_path ${SECRET_FILE_PATH} --configuration_file_full_path ${CONFIGURATION_FILE_PATH}

get_secret_file:
	source ${VENV_BIN_DIR}/activate &&\
	export PYTHONPATH=${AWS_API_DIR} &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action get_secret_file --secret_name ${SECRET_FILE_NAME} --secret_file_path ${SECRET_FILE_PATH} --configuration_file_full_path ${CONFIGURATION_FILE_PATH}

push_sns:
	source ${VENV_BIN_DIR}/activate &&\
	python3 ${AWS_API_CLIENTS_DIR}/sns_client_actor.py --action publish --topic_arn "arn:aws:sns:us-east-1" --subject "zabbix-test-from-local" --message "please ignore" --accounts_file "managed_accounts.py" --account "1"
	#export AWS_PROFILE=current
