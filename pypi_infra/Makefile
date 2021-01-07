
SHELL := /bin/bash

SRC_DIR= /Users/alexeybe/private
BUILD_DIR= ${SRC_DIR}/_build
VENV_DIR= ${BUILD_DIR}/_venv
ZIP_FILE= ${BUILD_DIR}/function.zip

REQUIREMENTS=~/private/IP

ALL_FILES := $(wildcard *)
EXCLUSIONS := Makefile _build
SRC_FILES := $(filter-out $(EXCLUSIONS), $(ALL_FILES))

TMP_CREDENTIALS_FILE := aws_auth_info.json
IMAGE_ID := 701464338db1
REPO_NAME := "horey-pypi"
IMAGE_TAG := "latest"

deploy_ecs: create_task_definition

update_ecs_service:
	python3 aws_api_actor.py --action update_ecs_service --task_definition_name ${TASK_DEFINITION_NAME}

upload_image: create_repository save_credentials docker_login tag_image push_image

create_repository:
	python3 ecr_client_actor.py --action create_repository --repository_name ${REPO_NAME}

save_credentials:
	python3 ecr_client_actor.py --action get_authorization_information --output_file_name ${TMP_CREDENTIALS_FILE}


docker_login_bash:
	$(eval AWS_TOKEN=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,decoded_token")) \
    $(eval USER_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,user_name")) \
    $(eval HOST_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,proxy_host")) \
    echo "${AWS_TOKEN}" | docker login --username ${USER_NAME} --password-stdin ${HOST_NAME}


tag_image:
	$(eval HOST_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,proxy_host")) \
	docker tag ${IMAGE_ID} ${HOST_NAME}/${REPO_NAME}


push_image_bash:
	docker push ${HOST_NAME}/${REPO_NAME}



venv_dir:
	mkdir -p ${BUILD_DIR}
	python3 -m venv ${VENV_DIR} && \
	pip3 install pylint &&\
	pip3 install wheel &&\
	pip3 install docker

package_source_requirements: venv_dir
	for VARIABLE in ${REQUIREMENTS}; do \
	cd $$VARIABLE; \
	rm -rf $$VARIABLE\dist; \
	python3 setup.py sdist bdist_wheel; \
	done

install_source_requirements: package_source_requirements
	source ${VENV_DIR}/bin/activate && \
	for VARIABLE in ${REQUIREMENTS}; do \
	cd $$VARIABLE; \
	pip3 install dist/*.whl; \
	done

clear_zip:
	rm -rf ${SRC_DIR}/function.zip

zip_src: install_source_requirements clear_zip
	cd ${VENV_DIR}/lib/python3.7/site-packages &&\
	zip -r9 ${ZIP_FILE} . &&\
	cd ${SRC_DIR} && \
	for SRC_FILE in ${SRC_FILES}; do \
	zip -g ${ZIP_FILE} $$SRC_FILE; \
	done

invoke: install_source_requirements
	source ${VENV_DIR}/bin/activate &&\
	python3 invoke_me.py

raw_invoke:
	source ${VENV_DIR}/bin/activate &&\
	python3 invoke_me.py

build_image:
	source ${VENV_DIR}/bin/activate &&\
	$(eval HOST_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,proxy_host")) \
	python3 docker_actor.py --action build --tag ${HOST_NAME}/${REPO_NAME}:${IMAGE_TAG}

docker_login_python:
	$(eval AWS_TOKEN=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,decoded_token")) \
    $(eval USER_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,user_name")) \
    $(eval HOST_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,proxy_host")) \
    python3 docker_actor.py --action login --host ${HOST_NAME} --username ${USER_NAME} --password "${AWS_TOKEN}"


push_image_python:
	$(eval AWS_TOKEN=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,decoded_token")) \
    $(eval USER_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,user_name")) \
    $(eval HOST_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,proxy_host")) \
	python3 docker_actor.py --action push --repository ${HOST_NAME}/${REPO_NAME} --tag ${IMAGE_TAG} --host ${HOST_NAME} --username ${USER_NAME} --password "${AWS_TOKEN}"


run:
	$(eval HOST_NAME=$(shell python3 json_actor.py --action extract --file_name ${TMP_CREDENTIALS_FILE} --path "0,proxy_host"))
	docker run -it -p 8080:8080  ${HOST_NAME}/${REPO_NAME}:${IMAGE_TAG} /bin/bash

clear:
	rm -rf ${VENV_DIR}

pylint: venv_dir pylint_raw

raw_pylint:
	source ${VENV_DIR}/bin/activate &&\
	pylint ${SRC_DIR}/aws_api/src/aws_api.py
	#pylint ${SRC_FILES}


create_kms_key:
	python3 kms_client_actor.py --action create_key --name common-pypi-key

create_codeartifact_create_domain:
	python3 codeartifact_client_actor.py --action create_domain --name common-pypi-domain --encryption_key_alias alias/common-pypi-key

create_codeartifact_create_repository:
	python3 codeartifact_client_actor.py --action create_repository --domain_name common-pypi-domain --repository_name common-pypi-repository

create_dns_record:
	python3 route53_client_actor.py --action create_record --name common-pypi-key

get_repository_endpoint:
	python3 codeartifact_client_actor.py --action get_repository_endpoint --domain_name common-pypi-domain --repository_name common-pypi-repository --format pypi