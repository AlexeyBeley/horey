SHELL := /bin/bash
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SRC_DIR := ${ROOT_DIR}/../horey/deployer

REMOTE_DEPLOYER_SCRIPT_PATH := ${ROOT_DIR}/script_deployer_test.sh
STEP_SCRIPT_CONFIGURATION_FILE_PATH=${ROOT_DIR}/script_deployer_configuration.json
STEP_SCRIPT_FINISH_STATUS_FILE=${ROOT_DIR}/deploy_step_finish_status
STEP_SCRIPT_OUTPUT_FILE_PATH=${ROOT_DIR}/deploy_step_output.txt

test:
	${SRC_DIR}/remote_step_executor.sh ${REMOTE_DEPLOYER_SCRIPT_PATH} ${STEP_SCRIPT_CONFIGURATION_FILE_PATH} ${STEP_SCRIPT_FINISH_STATUS_FILE} ${STEP_SCRIPT_OUTPUT_FILE_PATH}

VENV_BIN_DIR := ${ROOT_DIR}/../build/_build/_venv/bin

aws_api_init_and_cache-%:
	source ${VENV_BIN_DIR}/activate &&\
	export PYTHONPATH=${AWS_API_DIR} &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action init_and_cache --target $(subst aws_api_init_and_cache-,,$@) --configuration_file_full_path ${CONFIGURATION_FILE_PATH}

test_machine_deployment_step:
	python3 ./test_machine_deployment_step.py