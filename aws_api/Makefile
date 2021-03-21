
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ACCOUNTS_FILE_PATH := ${ROOT_DIR}/../aws_api/ignore/ignore_me.py
AWS_API_DIR := ${ROOT_DIR}/horey/aws_api
AWS_API_CLIENTS_DIR := ${AWS_API_DIR}/aws_clients
VENV_DIR := ${ROOT_DIR}/../build/_build/_venv/bin


aws_api_cleanup-%:
	source ${VENV_DIR}/activate &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action cleanup --target $(subst aws_api_cleanup-,,$@) --accounts_file_path ${ACCOUNTS_FILE_PATH} --account_id 0 --regions all

aws_api_cache-%:
	source ${VENV_DIR}/activate &&\
	export PYTHONPATH=${AWS_API_DIR} &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action init_and_cache --target $(subst aws_api_cache-,,$@) --configuration_file_path ${ACCOUNTS_FILE_PATH}

aws_api_sts_set:
	source ${VENV_DIR}/activate &&\
	python3 ${AWS_API_CLIENTS_DIR}/session_manager_actor.py --action set_session_credentials --profile_name current --configuration_file_full_path ${ACCOUNTS_FILE_PATH}

#export AWS_PROFILE=current