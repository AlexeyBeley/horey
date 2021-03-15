
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ACCOUNTS_FILE_PATH := ${ROOT_DIR}/../aws_api/ignore/ignore_me.py
AWS_API_DIR := ${ROOT_DIR}/horey/aws_api
VENV_DIR := ${ROOT_DIR}/../build/_build/_venv/bin


aws_api_cleanup-%:
	source ${VENV_DIR}/activate &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action cleanup --target $(subst aws_api_cleanup-,,$@) --accounts_file_path ${ACCOUNTS_FILE_PATH} --account_id 0 --regions all

aws_api_cache-%:
	source ${VENV_DIR}/activate &&\
	export PYTHONPATH=${AWS_API_DIR} &&\
	python3 ${AWS_API_DIR}/aws_api_actor.py --action init_and_cache --target $(subst aws_api_cache-,,$@) --configuration_file_path ${ACCOUNTS_FILE_PATH}

