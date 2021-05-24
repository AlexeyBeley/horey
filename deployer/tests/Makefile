
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SRC_DIR := ${ROOT_DIR}/../horey/deployer

REMOTE_DEPLOYER_SCRIPT_PATH := ${ROOT_DIR}/script_deployer_test.sh
STEP_SCRIPT_CONFIGURATION_FILE_PATH=${ROOT_DIR}/script_deployer_configuration.json
STEP_SCRIPT_FINISH_STATUS_FILE=${ROOT_DIR}/deploy_step_finish_status
STEP_SCRIPT_OUTPUT_FILE_PATH=${ROOT_DIR}/deploy_step_output.txt

test:
	${SRC_DIR}/remote_step_executor.sh ${REMOTE_DEPLOYER_SCRIPT_PATH} ${STEP_SCRIPT_CONFIGURATION_FILE_PATH} ${STEP_SCRIPT_FINISH_STATUS_FILE} ${STEP_SCRIPT_OUTPUT_FILE_PATH}
